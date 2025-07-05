import uuid
from datetime import datetime

from sqlalchemy import ( Column, String, Boolean, DateTime, ForeignKey,
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 

class Media(Base):
    __tablename__ = "media"
    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False) # Owner of the media
    url = Column(String(255), nullable=False)
    media_type = Column(String(10), nullable=False) # 'image', 'video'
    moment_id = Column(UUID(as_uuid=True), ForeignKey("moments.moment_id", ondelete="CASCADE"), nullable=True) # Optional: if linked to a moment
    is_public = Column(Boolean, default=True, nullable=False) # Can be private media
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    moment = relationship("Moment", back_populates="media")
