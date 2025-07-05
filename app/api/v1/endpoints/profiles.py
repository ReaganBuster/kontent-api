from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.schemas.user import UserPublic
from app.services.profile_service import ProfileService as crud_profile
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
def read_my_profile(current_user: crud_user.get_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # The profile is loaded via relationship on current_user
    if not current_user.profile:
        # This shouldn't happen if profile is created with user, but as a fallback
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found for current user")
    return current_user.profile

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(profile_in: ProfileUpdate, current_user: crud_user.get_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found for current user")
    
    # Handle updating profile picture
    if profile_in.profile_picture_id:
        # Verify ownership of the media
        media_item = db.query(crud_profile.Media).filter(
            crud_profile.Media.media_id == profile_in.profile_picture_id,
            crud_profile.Media.user_id == current_user.user_id
        ).first()
        if not media_item:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or unauthorized profile picture media ID.")
        current_user.profile.profile_media_id = profile_in.profile_picture_id
        # Optionally, set profile_picture_url directly if Media model has it or if you manage S3 URLs
        current_user.profile.profile_picture_url = media_item.url # This would be dynamically updated

    return crud_profile.update_profile(db, db_profile=current_user.profile, profile_in=profile_in)

@router.get("/{user_id}", response_model=ProfileResponse)
def read_public_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    # This endpoint is for viewing other users' profiles
    profile = crud_profile.get_profile_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    # You might add checks here if the profile is not "discoverable" or if user has blocked them
    if not profile.is_searchable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found or is private")
        
    return profile