from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.flirt import FlirtCreate, FlirtResponse
from app.services.flirt_service import FlirtService as crud_flirt
from app.services.moment_service import MomentService as crud_moment
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.post("/", response_model=FlirtResponse, status_code=status.HTTP_201_CREATED)
def create_flirt(
    flirt_in: FlirtCreate,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Flirt with a moment (like a 'like' or 'heart')."""
    moment = crud_moment.get_moment(db, moment_id=flirt_in.moment_id)
    if not moment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
    
    # Optional: Prevent flirter from flirting with their own moment
    if moment.user_id == current_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot flirt with your own moment.")

    try:
        db_flirt = crud_flirt.create_flirt(db, flirter_id=current_user.user_id, moment_id=flirt_in.moment_id)
        # You might also create a notification for the moment's author here
        # crud_notification.create_notification(...)
        return db_flirt
    except Exception as e: # Catch potential UniqueConstraintError if already flirted
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already flirted with this moment.")

@router.delete("/{flirt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flirt(
    flirt_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a flirt (unlike)."""
    db_flirt = crud_flirt.get_flirt(db, flirt_id=flirt_id)
    if not db_flirt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flirt not found")
    if db_flirt.flirter_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this flirt")
    
    crud_flirt.delete_flirt(db, flirt_id=flirt_id)
    return