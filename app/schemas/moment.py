from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from app.schemas.user import UserPublic
from app.schemas.media import MediaResponse


# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)

# --- 4. Moment Schemas (The "Posts") ---
class MomentBase(BaseModel):
    text_content: Optional[str] = Field(None, max_length=1000)
    visibility: Optional[str] = Field("PUBLIC", pattern="^(PUBLIC|SUBSCRIBERS_ONLY|PRIVATE)$")
    # For creation, client provides media_ids, not direct media objects
    media_ids: Optional[List[uuid.UUID]] = None

    @model_validator(mode='after')
    def check_content(self):
        if not self.text_content and not self.media_ids:
            raise ValueError("Moment must have either text_content or media_ids")
        return self

class MomentCreate(MomentBase):
    pass

class MomentUpdate(BaseModel):
    text_content: Optional[str] = Field(None, max_length=1000)
    visibility: Optional[str] = Field(None, pattern="^(PUBLIC|SUBSCRIBERS_ONLY|PRIVATE)$")
    # For updates, client might send a list of new/existing media IDs or an empty list to clear
    media_ids: Optional[List[uuid.UUID]] = None

class MomentInDBBase(MomentBase):
    moment_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    flirt_count: int
    connection_attempt_count: int
    # Note: media_ids is not an ORM field, it's for input.
    # We will load actual media objects into the response schema

    model_config = ORMConfig

# Full Moment Response schema (for detailed view)
class MomentResponse(MomentInDBBase):
    author: UserPublic # Nested simplified author info
    media: List[MediaResponse] = [] # Nested list of media objects

    model_config = ORMConfig

# Simplified Moment for embedding (e.g., in a Connection response)
class MomentSimple(BaseModel):
    moment_id: uuid.UUID
    text_content: Optional[str] = None
    first_media_url: Optional[str] = None # Just the first image for a preview

    model_config = ORMConfig
    