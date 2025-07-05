import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ( Column, Integer, String, Boolean, DateTime, ForeignKey, Text,
    Numeric, UniqueConstraint
)
from app.core.database import Base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID 


# 2. Profile Model: Public user details, linked 1-to-1 with User
class Profile(Base):
    __tablename__ = "profiles"
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True) # User-chosen name
    bio = Column(Text, nullable=True)
    gender = Column(String(20), nullable=True) # e.g., 'male', 'female', 'non-binary'
    sexual_orientation = Column(String(50), nullable=True) # e.g., 'straight', 'gay', 'bisexual'
    age = Column(Integer, nullable=True) # Derived from DOB or explicitly set
    location = Column(String(100), nullable=True) # For location-based matching
    profile_media_id = Column(UUID(as_uuid=True), ForeignKey("media.media_id"), nullable=True) # Main profile pic
    looking_for = Column(String(50), nullable=True) # e.g., 'dating', 'hookup', 'friends'
    is_searchable = Column(Boolean, default=True, nullable=False) # Can other users find them?

    # Relationships
    user = relationship("User", back_populates="profile")
    profile_picture = relationship("Media", foreign_keys=[profile_media_id], uselist=False)