from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

ORMConfig = ConfigDict(from_attributes=True)

class MediaBase(BaseModel):
    url: str = Field(..., max_length=255)
    media_type: str = Field(..., pattern="^(image|video)$")
    is_public: Optional[bool] = True

class MediaUpload(MediaBase): # For client uploading media
    # Client provides URL (e.g., from pre-signed S3 upload) and type
    pass

class MediaResponse(MediaBase):
    media_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    moment_id: Optional[uuid.UUID] = None # Will be populated if linked to a moment

    model_config = ORMConfig