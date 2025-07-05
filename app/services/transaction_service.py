from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from typing import List, Optional
import uuid
from decimal import Decimal

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def get_transaction(self, transaction_id: uuid.UUID) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

    def get_transactions_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

    def create_transaction(self, user_id: uuid.UUID, transaction_in: TransactionCreate, status: str = "PENDING", connection_id: Optional[uuid.UUID] = None) -> Transaction:
        db_transaction = Transaction(
            user_id=user_id,
            connection_id=connection_id,
            amount=Decimal(str(transaction_in.amount)), # Ensure Decimal type for accuracy
            currency=transaction_in.currency,
            status=status, # Initial status from backend
            payment_method=transaction_in.payment_method,
            external_id=transaction_in.external_id
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def update_transaction_status(self, transaction_id: uuid.UUID, new_status: str, external_id: Optional[str] = None) -> Optional[Transaction]:
        db_transaction = self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if db_transaction:
            db_transaction.status = new_status
            if external_id:
                db_transaction.external_id = external_id
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            return db_transaction
        return None