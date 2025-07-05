import uuid
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, String, Boolean, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"
    settings_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Notification preferences
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    push_notifications_enabled = Column(Boolean, default=True, nullable=False)
    notify_new_flirt = Column(Boolean, default=True, nullable=False)
    notify_connection_request = Column(Boolean, default=True, nullable=False)
    notify_connection_accepted = Column(Boolean, default=True, nullable=False)
    notify_new_message = Column(Boolean, default=True, nullable=False)
    notify_earning_paid = Column(Boolean, default=True, nullable=False)
    
    # Privacy settings
    show_online_status = Column(Boolean, default=True, nullable=False)
    allow_dm_from_unconnected = Column(Boolean, default=False, nullable=False) # Should be false, only allow DMs post-connection
    discoverable = Column(Boolean, default=True, nullable=False) # Can user be found in search/browse
    
    # Display preferences
    theme_preference = Column(String(20), default="light", nullable=False) # 'light', 'dark'
    
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Use DB trigger

    # Relationship
    user = relationship("User", back_populates="settings")