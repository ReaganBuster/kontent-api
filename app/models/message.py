import uuid
from datetime import datetime

from sqlalchemy import ( Column, Boolean, DateTime, ForeignKey, Text,
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 


# 7. Message Model: Direct messages within an active Connection
class Message(Base):
    __tablename__ = "messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.connection_id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    text_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False) # Tracks if recipient has read

    # Relationships
    connection = relationship("Connection", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages") # assuming User has a 'sent_messages' back_populates

