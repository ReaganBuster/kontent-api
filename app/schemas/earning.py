from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)

class EarningResponse(BaseModel):
    earning_id: uuid.UUID
    user_id: uuid.UUID # The recipient of the earning (poster)
    connection_id: uuid.UUID
    amount: float
    currency: str
    status: str
    created_at: datetime
    paid_out_at: Optional[datetime] = None
    payout_transaction_id: Optional[uuid.UUID] = None

    model_config = ORMConfig
    
class EarningCreate(BaseModel):
    user_id: uuid.UUID # The recipient of the earning (poster)
    connection_id: uuid.UUID
    amount: float
    currency: str = "USD" # Default currency
    status: str = "PENDING" # Initial status

    @model_validator(mode="before")
    def validate_amount(cls, values):
        if values.get("amount", 0) <= 0:
            raise ValueError("Amount must be greater than zero.")
        return values

    model_config = ORMConfig