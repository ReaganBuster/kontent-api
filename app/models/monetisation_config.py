import uuid
from datetime import datetime

from sqlalchemy import ( Column, String, Boolean, DateTime, 
    Numeric
)
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID 


# 10. MonetizationConfig (New table for platform-wide monetization rules)
class MonetizationConfig(Base):
    __tablename__ = "monetization_configs"
    config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_name = Column(String(50), unique=True, nullable=False) # e.g., "DM_FEE_STANDARD", "PROMO_RATE"
    connection_fee_base = Column(Numeric(10, 2), nullable=False) # Base fee for a connection
    platform_cut_percentage = Column(Numeric(5, 2), nullable=False) # e.g., 0.20 for 20%
    poster_share_percentage = Column(Numeric(5, 2), nullable=False) # e.g., 0.80 for 80%
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Use DB trigger