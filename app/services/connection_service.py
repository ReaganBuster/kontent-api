from sqlalchemy.orm import Session
from app.models.connection import Connection
from app.models.moment import Moment
from app.models.user import User
from app.models.monetisation_config import MonetizationConfig
from app.schemas.connection import ConnectionRequest, ConnectionStatusUpdate
from typing import Optional, Tuple
import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from app.services.earning_service import EarningService
from app.services.transaction_service import TransactionService
from app.services.notification_service import NotificationService
from app.schemas.monetisation import MonetizationConfigBase
from app.schemas.transaction import TransactionCreate


class ConnectionService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_connection(self, connection_id: uuid.UUID) -> Optional[Connection]:
        return self.db.query(Connection).filter(Connection.connection_id == connection_id).first()

    def get_pending_connection(self, requester_id: uuid.UUID, recipient_id: uuid.UUID, moment_id: Optional[uuid.UUID] = None) -> Optional[Connection]:
        """Check for an existing PENDING_PAYMENT connection between two users for a specific moment."""
        query = self.db.query(Connection).filter(
            Connection.requester_id == requester_id,
            Connection.recipient_id == recipient_id,
            Connection.status == "PENDING_PAYMENT"
        )
        if moment_id:
            query = query.filter(Connection.moment_id == moment_id)
        return query.first()

    def calculate_connection_fees(self, config_name: str = "DM_FEE_STANDARD") -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculates the base fee, platform cut, and poster share based on active monetization config.
        """
        config = self.db.query(MonetizationConfig).filter(
            MonetizationConfig.config_name == config_name,
            MonetizationConfig.is_active == True
        ).first()

        if not config:
            raise ValueError(f"Monetization configuration '{config_name}' not found or not active.")

        base_fee = config.connection_fee_base
        platform_cut = base_fee * config.platform_cut_percentage
        poster_share = base_fee * config.poster_share_percentage

        return base_fee, platform_cut, poster_share

    def create_connection_request(self, requester_id: uuid.UUID, connection_in: ConnectionRequest) -> Tuple[Connection, Decimal]:
        """
        Creates a new connection request, calculates fees, and sets initial status.
        Returns the new connection and the total amount to be paid by the requester.
        """
        recipient = self.db.query(User).filter(User.user_id == connection_in.recipient_id).first()
        if not recipient:
            raise ValueError("Recipient user not found.")

        if requester_id == connection_in.recipient_id:
            raise ValueError("Cannot initiate a connection with yourself.")

        # Check for existing pending connection to prevent duplicates
        existing_connection = self.get_pending_connection(self.db, requester_id, connection_in.recipient_id, connection_in.moment_id)
        if existing_connection:
            return existing_connection, existing_connection.fee_amount # Return existing and its fee

        # Calculate fees (you might retrieve the active config dynamically)
        try:
            fee_amount, platform_cut, poster_share = self.calculate_connection_fees(self.db)
        except ValueError as e:
            raise ValueError(f"Fee calculation failed: {e}")

        db_connection = Connection(
            requester_id=requester_id,
            recipient_id=connection_in.recipient_id,
            moment_id=connection_in.moment_id,
            status="PENDING_PAYMENT",
            fee_amount=fee_amount,
            platform_cut=platform_cut,
            poster_share=poster_share
        )
        self.db.add(db_connection)
        self.db.commit()
        self.db.refresh(db_connection)
        
        return db_connection, fee_amount

    def update_connection_status(self, connection_id: uuid.UUID, new_status: str) -> Optional[Connection]:
        db_connection = self.db.query(Connection).filter(Connection.connection_id == connection_id).first()
        if not db_connection:
            return None
        
        # Basic state transitions (more complex logic in a service layer often)
        if new_status in ["ACCEPTED", "DECLINED", "CANCELED"]:
            db_connection.status = new_status
            self.db.add(db_connection)
            self.db.commit()
            self.db.refresh(db_connection)
            return db_connection
        return None # Or raise for invalid status transition

    def initiate_paid_connection(self, requester_id: uuid.UUID, connection_request: ConnectionRequest) -> Connection:
        """
        Handles the initiation of a paid connection request.
        Creates the connection entry and determines the amount to be paid.
        """
        # This will create a PENDING_PAYMENT connection
        db_connection, amount_to_pay = self.crud_connection.create_connection_request(
            self.db, requester_id, connection_request
        )
        # You'd typically return the connection info and the amount to the frontend
        # for them to proceed with payment.
        return db_connection # Frontend gets this and prompts for payment

    def process_payment_and_activate_connection(self, connection_id: uuid.UUID, transaction_data: TransactionCreate) -> Connection:
        """
        Called after successful payment gateway response.
        Updates connection status and creates transaction record.
        """
        db_connection = self.crud_connection.get_connection(self.db, connection_id)
        if not db_connection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

        if db_connection.status != "PENDING_PAYMENT":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connection is not in pending payment state.")

        # 1. Record the successful transaction
        db_transaction = TransactionService.create_transaction(
            self.db,
            user_id=db_connection.requester_id, # The payer
            transaction_in=transaction_data,
            connection_id=connection_id,
            status="SUCCESS"
        )

        # 2. Update connection status to PAID (pending recipient's acceptance)
        db_connection.status = "PAID_PENDING_ACCEPT"
        self.db.add(db_connection)
        self.db.commit()
        self.db.refresh(db_connection)

        # 3. Notify the recipient of a new paid connection request
        recipient_user = self.db.query(User).filter(User.user_id == db_connection.recipient_id).first()
        if recipient_user:
            NotificationService.create_notification(
                self.db,
                recipient_id=db_connection.recipient_id,
                sender_id=db_connection.requester_id,
                type="CONNECTION_REQUEST",
                title="New Connection Request!",
                message=f"{db_connection.requester.username} has paid to connect with you. Accept to chat!",
                entity_id=db_connection.connection_id,
                entity_type="connection"
            )
        return db_connection

    def handle_recipient_response(self, connection_id: uuid.UUID, recipient_id: uuid.UUID, status_update: ConnectionStatusUpdate) -> Connection:
        """
        Handles the recipient's acceptance or decline of a paid connection.
        """
        db_connection = self.get_connection(self.db, connection_id)
        if not db_connection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

        if db_connection.recipient_id != recipient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the recipient of this connection.")

        if db_connection.status != "PAID_PENDING_ACCEPT":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Connection is not pending acceptance. Current status: {db_connection.status}")

        new_status = status_update.status

        if new_status == "ACCEPTED":
            db_connection.status = "ACCEPTED"
            # Create an earning record for the recipient (poster)
            EarningService.create_earning(
                self.db,
                user_id=db_connection.recipient_id,
                connection_id=db_connection.connection_id,
                amount=db_connection.poster_share # Amount to be earned by poster
            )
            # Notify requester that their connection was accepted
            NotificationService.create_notification(
                self.db,
                recipient_id=db_connection.requester_id,
                sender_id=db_connection.recipient_id,
                type="CONNECTION_ACCEPTED",
                title="Connection Accepted!",
                message=f"{db_connection.recipient.username} has accepted your connection request. You can now chat!",
                entity_id=db_connection.connection_id,
                entity_type="connection"
            )
        elif new_status == "DECLINED":
            db_connection.status = "DECLINED"
            # Here, you'd trigger a refund process for the requester
            # (Logic for refunding would go in transaction service)
            NotificationService.create_notification(
                self.db,
                recipient_id=db_connection.requester_id,
                sender_id=db_connection.recipient_id,
                type="CONNECTION_DECLINED",
                title="Connection Declined",
                message=f"{db_connection.recipient.username} has declined your connection request.",
                entity_id=db_connection.connection_id,
                entity_type="connection"
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status update for this context.")

        self.db.add(db_connection)
        self.db.commit()
        self.db.refresh(db_connection)
        return db_connection