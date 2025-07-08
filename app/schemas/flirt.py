from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

ORMConfig = ConfigDict(from_attributes=True)

class FlirtCreate(BaseModel):
    moment_id: uuid.UUID

class FlirtResponse(BaseModel):
    flirt_id: uuid.UUID
    flirter_id: uuid.UUID
    moment_id: uuid.UUID
    created_at: datetime
    
    # Optional: include flirter info
    # flirter: UserPublic

    model_config = ORMConfig