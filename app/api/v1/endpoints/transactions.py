from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import TransactionService as crud_transaction
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.get("/me", response_model=List[TransactionResponse])
def get_my_transactions(
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    """Retrieve all transactions initiated by the current user."""
    return crud_transaction.get_transactions_by_user(db, user_id=current_user.user_id, skip=skip, limit=limit)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_details(
    transaction_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a specific transaction, only if owned by current user."""
    transaction = crud_transaction.get_transaction(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this transaction.")
    return transaction

# Note: Transaction creation is typically handled internally by the ConnectionService
# after a payment gateway confirms success, not directly exposed via a POST endpoint for users.