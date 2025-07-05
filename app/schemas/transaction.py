from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)


# --- 8. Transaction Schemas ---
class TransactionCreate(BaseModel):
    connection_id: uuid.UUID
    amount: float = Field(gt=0.0)
    currency: str = Field("USD", max_length=3)
    payment_method: str = Field(..., max_length=50) # e.g., "Stripe_Card"
    external_id: Optional[str] = Field(None, max_length=100) # Payment gateway transaction ID

class TransactionResponse(BaseModel):
    transaction_id: uuid.UUID
    user_id: uuid.UUID # User who made the payment
    connection_id: Optional[uuid.UUID] = None
    amount: float
    currency: str
    status: str
    payment_method: Optional[str] = None
    transaction_date: datetime
    external_id: Optional[str] = None

    model_config = ORMConfig