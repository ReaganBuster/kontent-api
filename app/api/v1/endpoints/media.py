from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.media import MediaUpload, MediaResponse
from app.services.media_service import MediaService
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.post("/", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    media_data: MediaUpload,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register media uploaded by the client (e.g., to S3 via pre-signed URL).
    This only records the URL and metadata in the database.
    Actual file upload happens directly from client to cloud storage.
    """
    # In a real app, you might generate a pre-signed URL here, send it to client,
    # client uploads, then client sends *this* request to register the completed upload.
    # For now, we assume `media_data.url` is the final URL.
    
    crud_media = MediaService(db)
    db_media = crud_media.create_media(media=media_data, user_id=current_user.user_id)
    return db_media

@router.get("/me", response_model=List[MediaResponse])
def get_my_media(
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    """Retrieve all media uploaded by the current user."""
    crud_media = MediaService(db)
    return crud_media.get_media_by_user(user_id=current_user.user_id, skip=skip, limit=limit)

@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific media item by its ID."""
    crud_media = MediaService(db)
    db_media = crud_media.get_media(media_id=media_id)
    if not db_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
    if db_media.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this media")
    
    # In a real app, you would also trigger deletion from cloud storage here
    crud_media.delete_media(media_id=media_id)
    return