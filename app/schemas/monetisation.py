from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional, List, Dict
import uuid
from datetime import datetime

# --- General Base Config for Pydantic v2 ---
# This is crucial for handling ORM objects (SQLAlchemy instances)
ORMConfig = ConfigDict(from_attributes=True)


class MonetizationConfigBase(BaseModel):
    config_name: str = Field(..., max_length=50)
    connection_fee_base: float = Field(gt=0.0)
    platform_cut_percentage: float = Field(ge=0.0, le=1.0) # As a decimal, e.g., 0.20
    poster_share_percentage: float = Field(ge=0.0, le=1.0) # As a decimal, e.g., 0.80

    @model_validator(mode='after')
    def check_percentages(self):
        # Ensure platform_cut + poster_share equals 100%
        if self.platform_cut_percentage + self.poster_share_percentage != 1.0:
            raise ValueError("Platform cut percentage and poster share percentage must sum to 1.0 (100%)")
        return self

class MonetizationConfigResponse(MonetizationConfigBase):
    config_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ORMConfig


# --- Forward References for Recursive Models ---
# This is crucial for Pydantic to resolve circular dependencies where models
# might reference each other
# UserResponse.model_rebuild()