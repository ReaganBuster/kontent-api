from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from app.schemas.user import UserPublic

# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)


# --- 7. Message Schemas ---
class MessageCreate(BaseModel):
    connection_id: uuid.UUID
    text_content: str = Field(min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    message_id: uuid.UUID
    connection_id: uuid.UUID
    sender_id: uuid.UUID
    text_content: str
    created_at: datetime
    is_read: bool
    sender: UserPublic # Nested simplified sender info

    model_config = ORMConfig