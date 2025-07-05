from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user_settings import UserSettingsUpdate, UserSettingsResponse
from app.services.user_service import UserService as crud_user
from app.services.user_settings_service import UserSettingsService as crud_settings
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.get("/me", response_model=UserSettingsResponse)
def get_my_settings(current_user: crud_user.get_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve the current user's settings."""
    if not current_user.settings:
        # Should ideally be created upon user creation
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user settings not found.")
    return current_user.settings

@router.put("/me", response_model=UserSettingsResponse)
def update_my_settings(
    settings_in: UserSettingsUpdate,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's settings."""
    if not current_user.settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user settings not found.")
    
    updated_settings = crud_settings.update_user_settings(db, db_settings=current_user.settings, settings_in=settings_in)
    return updated_settings