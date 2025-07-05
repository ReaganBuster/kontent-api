from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.earning import EarningResponse
from app.services.earning_service import EarningService as crud_earning
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.get("/me", response_model=List[EarningResponse])
def get_my_earnings(
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    """Retrieve all earnings for the current user (poster's share from connections)."""
    return crud_earning.get_earnings_by_user(db, user_id=current_user.user_id, skip=skip, limit=limit)

@router.get("/{earning_id}", response_model=EarningResponse)
def get_earning_details(
    earning_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a specific earning, only if owned by current user."""
    earning = crud_earning.get_earning(db, earning_id=earning_id)
    if not earning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Earning not found")
    if earning.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this earning.")
    return earning

# Payout endpoint would typically be an ADMIN function or an internal job.
# @router.post("/{earning_id}/payout", response_model=EarningResponse)
# def request_payout(earning_id: uuid.UUID, current_user: crud_user.get_user = Depends(get_current_user), db: Session = Depends(get_db)):
#    ... complex logic for payout processing ...