import uuid
from datetime import datetime

from sqlalchemy import ( Column, String, DateTime, ForeignKey,
    Numeric
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 

class Earning(Base):
    __tablename__ = "earnings"
    earning_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # The user who is receiving the earning
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.connection_id"), unique=True, nullable=False) # Link to the specific connection
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), default="PENDING_PAYOUT", nullable=False) # PENDING_PAYOUT, PAID_OUT, CANCELED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    paid_out_at = Column(DateTime, nullable=True)
    payout_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"), nullable=True) # Link to platform payout transaction

    # Relationships
    recipient = relationship("User", back_populates="earnings")
    connection = relationship("Connection", back_populates="earning", uselist=False)
    payout_transaction = relationship("Transaction") # Unidirectional link for payout tracking