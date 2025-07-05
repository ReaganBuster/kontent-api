import uuid
from datetime import datetime

from sqlalchemy import ( Column, DateTime, ForeignKey, UniqueConstraint
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 

class Flirt(Base):
    __tablename__ = "flirts"
    flirt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flirter_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    moment_id = Column(UUID(as_uuid=True), ForeignKey("moments.moment_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('flirter_id', 'moment_id', name='_flirter_moment_uc'),) # One flirt per user per moment

    # Relationships
    flirter = relationship("User", back_populates="flirts_given")
    moment = relationship("Moment", back_populates="flirts")