import uuid
from datetime import datetime

from sqlalchemy import ( Column, Integer, String, DateTime, ForeignKey, Text
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 

# 3. Moment Model (Posts): The "bait"
class Moment(Base):
    __tablename__ = "moments"
    moment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    text_content = Column(Text, nullable=True) # Can be just text or text+media
    visibility = Column(String(20), default="PUBLIC", nullable=False) # PUBLIC, SUBSCRIBERS_ONLY, PRIVATE
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Use DB trigger
    # Denormalized counts for quick access (can be updated by triggers or events)
    flirt_count = Column(Integer, default=0, nullable=False)
    connection_attempt_count = Column(Integer, default=0, nullable=False) # How many DMs initiated from this moment

    # Relationships
    author = relationship("User", back_populates="moments")
    media = relationship("Media", back_populates="moment", cascade="all, delete-orphan") # One-to-many media for a moment
    flirts = relationship("Flirt", back_populates="moment", cascade="all, delete-orphan")