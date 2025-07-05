from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.connection import ConnectionRequest, ConnectionResponse, ConnectionStatusUpdate
from app.models.user import User # For notifications later
from app.services.connection_service import ConnectionService
from app.models.connection import Connection
from app.schemas.transaction import TransactionCreate

router = APIRouter()

# Dependency to get the ConnectionService instance
def get_connection_service(db: Session = Depends(get_db)):
    return ConnectionService(db)

@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_202_ACCEPTED) # 202 because payment pending
def request_connection(
    conn_request: ConnectionRequest,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Initiates a connection request. Returns the connection details and the amount to pay.
    The client then proceeds with payment.
    """
    try:
        db_connection = connection_service.initiate_paid_connection(
            requester_id=current_user.user_id,
            connection_request=conn_request
        )
        return db_connection
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{connection_id}/complete_payment", response_model=ConnectionResponse)
def complete_connection_payment(
    connection_id: uuid.UUID,
    transaction_data: TransactionCreate, # Data from client after payment
    current_user: User = Depends(get_current_user), # Ensure current user is the requester
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Endpoint for client to confirm successful payment for a connection.
    Updates connection status and triggers notifications.
    """
    db_connection = connection_service.process_payment_and_activate_connection(
        connection_id, transaction_data
    )
    if db_connection.requester_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only complete payment for your own connection requests.")
    
    return db_connection


@router.put("/{connection_id}/status", response_model=ConnectionResponse)
def update_connection_status(
    connection_id: uuid.UUID,
    status_update: ConnectionStatusUpdate,
    current_user: User = Depends(get_current_user), # Current user must be the recipient
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Recipient (poster) accepts or declines a paid connection request.
    """
    try:
        db_connection = connection_service.handle_recipient_response(
            connection_id=connection_id,
            recipient_id=current_user.user_id,
            status_update=status_update
        )
        return db_connection
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{connection_id}", response_model=ConnectionResponse)
def get_connection_details(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    connection = db.query(Connection).filter(Connection.connection_id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    # Ensure only requester or recipient can view details
    if current_user.user_id not in [connection.requester_id, connection.recipient_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this connection.")
    
    return connection