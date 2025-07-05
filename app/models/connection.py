import uuid
from datetime import datetime

from sqlalchemy import ( Column, String, DateTime, ForeignKey, Numeric, UniqueConstraint
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 

class Connection(Base):
    __tablename__ = "connections"
    connection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # User who wants to connect
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # User they want to connect with
    moment_id = Column(UUID(as_uuid=True), ForeignKey("moments.moment_id"), nullable=True) # Optional: if connection from specific moment
    
    status = Column(String(20), default="PENDING_PAYMENT", nullable=False) # PENDING_PAYMENT, PAID_PENDING_ACCEPT, ACCEPTED, DECLINED, CANCELED
    fee_amount = Column(Numeric(10, 2), nullable=False) # Total amount charged to requester
    platform_cut = Column(Numeric(10, 2), nullable=False)
    poster_share = Column(Numeric(10, 2), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Use DB trigger

    __table_args__ = (UniqueConstraint('requester_id', 'recipient_id', 'moment_id', name='_unique_connection_per_moment'),) # Only one connection request from A to B for a specific moment

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="connections_initiated")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="connections_received")
    moment = relationship("Moment") # Unidirectional or define back_populates on Moment
    messages = relationship("Message", back_populates="connection", cascade="all, delete-orphan") # Many-to-one
    transaction = relationship("Transaction", back_populates="connection", uselist=False) # One-to-one
    earning = relationship("Earning", back_populates="connection", uselist=False) # One-to-one