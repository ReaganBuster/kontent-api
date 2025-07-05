from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService as crud_message
from app.services.connection_service import ConnectionService as crud_connection
from app.services.notification_service import NotificationService as crud_notification
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    message_in: MessageCreate,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a new message within an established connection."""
    connection = crud_connection.get_connection(db, message_in.connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")
    
    # Ensure current user is part of this connection
    if current_user.user_id not in [connection.requester_id, connection.recipient_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this connection.")
    
    # Ensure connection is accepted before allowing messages
    if connection.status != "ACCEPTED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Messages can only be sent in an ACCEPTED connection.")

    try:
        db_message = crud_message.create_message(db, message_in=message_in, sender_id=current_user.user_id)
        
        # Notify the other party in the conversation
        other_user_id = connection.requester_id if connection.recipient_id == current_user.user_id else connection.recipient_id
        
        crud_notification.create_notification(
            db,
            recipient_id=other_user_id,
            sender_id=current_user.user_id,
            type="NEW_MESSAGE",
            title="New Message",
            message=f"You have a new message from {current_user.username}.",
            entity_id=db_message.message_id,
            entity_type="message"
        )
        return db_message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/connections/{connection_id}", response_model=List[MessageResponse])
def get_messages_in_connection(
    connection_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 50
):
    """Retrieve messages for a specific connection."""
    connection = crud_connection.get_connection(db, connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")
    
    # Ensure current user is part of this connection to view messages
    if current_user.user_id not in [connection.requester_id, connection.recipient_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this connection.")
    
    messages = crud_message.get_messages_by_connection(db, connection_id=connection_id, skip=skip, limit=limit)
    return messages

@router.put("/{message_id}/read", response_model=MessageResponse)
def mark_message_as_read(
    message_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user), # Recipient marks as read
    db: Session = Depends(get_db)
):
    """Mark a specific message as read."""
    db_message = crud_message.get_message(db, message_id=message_id)
    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")
    
    # Only the recipient can mark a message as read
    if db_message.sender_id == current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot mark your own sent messages as read.")
    if db_message.connection.recipient_id != current_user.user_id: # Assuming recipient is the 'other' user in conn
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to mark this message as read.")

    updated_message = crud_message.mark_message_as_read(db, message_id=message_id)
    if not updated_message: # Could be already read or not found initially
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message already read or not found.")
    return updated_message