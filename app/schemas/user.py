from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
import uuid

ORMConfig = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
class UserPublic(BaseModel):
    user_id: uuid.UUID
    username: str
    # display_name: Optional[str] = None # Pulled from profile
    # profile_picture_url: Optional[str] = None # Pulled from profile
    # is_online: Optional[bool] = None # Derived from last_active_at (e.g., within last 5 mins)

    model_config = ORMConfig

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
# UserResponse.model_rebuild()
