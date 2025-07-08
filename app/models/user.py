from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from sqlalchemy import ( Column, String, Boolean, DateTime )
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, configure_mappers

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications_sent = relationship("Notification", back_populates="sender", foreign_keys="[Notification.sender_id]")
    notifications_received = relationship("Notification", back_populates="recipient", foreign_keys="[Notification.recipient_id]")
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    moments = relationship("Moment", back_populates="author", cascade="all, delete-orphan")
    flirts_given = relationship("Flirt", back_populates="flirter")
    connections_initiated = relationship("Connection", foreign_keys="[Connection.requester_id]", back_populates="requester")
    connections_received = relationship("Connection", foreign_keys="[Connection.recipient_id]", back_populates="recipient")
    sent_messages = relationship("Message", back_populates="sender")
    transactions = relationship("Transaction", back_populates="payer")
    earnings = relationship("Earning", back_populates="recipient")
    

