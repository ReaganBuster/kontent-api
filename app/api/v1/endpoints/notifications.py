from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.services.notification_service import NotificationService as crud_notification
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.get("/me", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    read: Optional[bool] = None, # Filter by read status
    skip: int = 0, limit: int = 50
):
    """Retrieve notifications for the current user."""
    return crud_notification.get_notifications_by_recipient(db, recipient_id=current_user.user_id, read=read, skip=skip, limit=limit)

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    db_notification = crud_notification.get_notification(db, notification_id=notification_id)
    if not db_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    if db_notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this notification.")

    updated_notification = crud_notification.mark_notification_read_status(db, notification_id=notification_id, is_read=True)
    if not updated_notification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notification already read or could not be updated.")
    return updated_notification

@router.put("/{notification_id}/unread", response_model=NotificationResponse)
def mark_notification_as_unread(
    notification_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as unread."""
    db_notification = crud_notification.get_notification(db, notification_id=notification_id)
    if not db_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    if db_notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this notification.")

    updated_notification = crud_notification.mark_notification_read_status(db, notification_id=notification_id, is_read=False)
    if not updated_notification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notification already unread or could not be updated.")
    return updated_notification

@router.post("/mark_all_read", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_read(
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications for the current user as read."""
    notifications = crud_notification.get_notifications_by_recipient(db, recipient_id=current_user.user_id, read=False)
    for notif in notifications:
        crud_notification.mark_notification_read_status(db, notification_id=notif.notification_id, is_read=True)
    return