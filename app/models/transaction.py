import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ( Column, Integer, String, Boolean, DateTime, ForeignKey, Text,
    Numeric, UniqueConstraint
)
from app.core.database import Base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID 

# 8. Transaction Model: Records all payments
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # The user who made the payment
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.connection_id"), unique=True, nullable=True) # Direct link to connection
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, SUCCESS, FAILED, REFUNDED
    payment_method = Column(String(50), nullable=True) # e.g., "Stripe_Card", "PayPal"
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    external_id = Column(String(100), unique=True, nullable=True) # ID from payment gateway

    # Relationships
    payer = relationship("User", back_populates="transactions")
    connection = relationship("Connection", back_populates="transaction", uselist=False)