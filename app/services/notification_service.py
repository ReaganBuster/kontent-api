from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from typing import List, Optional
import uuid

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def update_notification(self, notification_id: uuid.UUID, notification_update: NotificationUpdate) -> Optional[Notification]:
        db_notification = self.get_notification(notification_id)
        if not db_notification:
            return None
        
        for key, value in notification_update.dict(exclude_unset=True).items():
            setattr(db_notification, key, value)
        
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def delete_notification(self, notification_id: uuid.UUID) -> bool:
        db_notification = self.get_notification(notification_id)
        if db_notification:
            self.db.delete(db_notification)
            self.db.commit()
            return True
        return False
    
    def get_notification(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        return db.query(Notification).filter(Notification.notification_id == notification_id).first()

    def get_notifications_by_recipient(db: Session, recipient_id: uuid.UUID, skip: int = 0, limit: int = 100, read: Optional[bool] = None) -> List[Notification]:
        query = db.query(Notification).filter(Notification.recipient_id == recipient_id)
        if read is not None:
            query = query.filter(Notification.is_read == read)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def create_notification(db: Session, recipient_id: uuid.UUID, type: str, title: str, message: str, sender_id: Optional[uuid.UUID] = None, entity_id: Optional[uuid.UUID] = None, entity_type: Optional[str] = None) -> Notification:
        db_notification = Notification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            type=type,
            title=title,
            message=message,
            entity_id=entity_id,
            entity_type=entity_type
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    def mark_notification_read_status(db: Session, notification_id: uuid.UUID, is_read: bool) -> Optional[Notification]:
        db_notification = db.query(Notification).filter(Notification.notification_id == notification_id).first()
        if db_notification:
            db_notification.is_read = is_read
            db.add(db_notification)
            db.commit()
            db.refresh(db_notification)
            return db_notification
        return None