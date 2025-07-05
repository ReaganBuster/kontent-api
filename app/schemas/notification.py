from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

# Assuming ORMConfig from previous response
ORMConfig = ConfigDict(from_attributes=True)

class NotificationCreate(BaseModel):
    recipient_id: uuid.UUID
    sender_id: Optional[uuid.UUID] = None # Optional, if system generated
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=100)
    message: str = Field(..., max_length=1000)
    entity_id: Optional[uuid.UUID] = None
    entity_type: Optional[str] = Field(None, max_length=50)

# For updating a notification (e.g., marking as read)
class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationResponse(BaseModel):
    notification_id: uuid.UUID
    recipient_id: uuid.UUID
    sender_id: Optional[uuid.UUID] = None
    type: str
    title: str
    message: str
    entity_id: Optional[uuid.UUID] = None
    entity_type: Optional[str] = None
    is_read: bool
    created_at: datetime

    # Optional: Embed sender info if 'sender_id' is present
    # sender: Optional['UserPublic'] = None # Requires UserPublic to be defined

    model_config = ORMConfig

# --- Important: Rebuild models if UserPublic (or other nested models) are defined after these ---
# If you place all schemas in a single file or import them correctly,
# you might need to rebuild UserResponse, PostResponse, ConnectionResponse, MessageResponse
# if they now optionally embed UserPublic, and UserPublic includes profile/media details.
# Example:
# from .user import UserPublic # If UserPublic is in user.py
# class MessageResponse(BaseModel):
#     # ... other fields ...
#     sender: UserPublic # Now Pydantic knows UserPublic

# Then at the bottom of your main schema file or after all models are defined:
# UserResponse.model_rebuild()
# NotificationResponse.model_rebuild() # If it embeds UserPublic