from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from app.schemas.user import UserPublic
from app.schemas.moment import MomentSimple


# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)


# --- 6. Connection Schemas (The paid link-up) ---
class ConnectionRequest(BaseModel):
    recipient_id: uuid.UUID # The user you want to connect with
    moment_id: Optional[uuid.UUID] = None # Optional: If initiated from a specific moment

class ConnectionStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(ACCEPTED|DECLINED|CANCELED)$")

class ConnectionInDBBase(BaseModel):
    connection_id: uuid.UUID
    requester_id: uuid.UUID
    recipient_id: uuid.UUID
    moment_id: Optional[uuid.UUID] = None
    status: str
    fee_amount: float
    platform_cut: float
    poster_share: float
    created_at: datetime
    updated_at: datetime

    model_config = ORMConfig

class ConnectionResponse(ConnectionInDBBase):
    requester: UserPublic
    recipient: UserPublic
    moment: Optional[MomentSimple] = None # Simplified moment if associated

    model_config = ORMConfig