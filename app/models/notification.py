import uuid
from datetime import datetime

from sqlalchemy import ( Column, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True) # Optional: if notification is from another user (e.g. new message, flirt)
    
    type = Column(String(50), nullable=False) # e.g., 'NEW_FLIRT', 'CONNECTION_REQUEST', 'MESSAGE_RECEIVED', 'EARNING_PAID'
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    
    # Optional: Link to the specific entity that triggered the notification
    entity_id = Column(UUID(as_uuid=True), nullable=True) # e.g., moment_id, connection_id, message_id
    entity_type = Column(String(50), nullable=True) # e.g., 'moment', 'connection', 'message'
    
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recipient = relationship("User", back_populates="notifications_received", foreign_keys=[recipient_id])
    sender = relationship("User", back_populates="notifications_sent", foreign_keys=[sender_id])