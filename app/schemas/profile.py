from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

ORMConfig = ConfigDict(from_attributes=True)

class ProfileBase(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    gender: Optional[str] = Field(None, max_length=20)
    sexual_orientation: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, gt=0, lt=100)
    location: Optional[str] = Field(None, max_length=100)
    looking_for: Optional[str] = Field(None, max_length=50) # e.g., 'dating', 'hookup', 'friends'
    is_searchable: Optional[bool] = True

class ProfileCreate(ProfileBase):
    pass # No extra fields for creation, linked to user_id directly

class ProfileUpdate(ProfileBase):
    profile_picture_id: Optional[uuid.UUID] = None # For assigning a media ID as profile pic

class ProfileResponse(ProfileBase):
    profile_id: uuid.UUID
    user_id: uuid.UUID
    profile_picture_url: Optional[str] = None # Full URL if available
    
    # Optional: Embed the associated UserPublic data if this is a response on its own
    # user: UserPublic

    model_config = ORMConfig