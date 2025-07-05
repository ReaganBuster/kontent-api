from sqlalchemy.orm import Session
from app.models.media import Media
from app.schemas.media import MediaUpload
from typing import List, Optional
import uuid
from datetime import datetime

class MediaService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_media(self, media_id: uuid.UUID) -> Optional[Media]:
        return self.db.query(Media).filter(Media.media_id == media_id).first()

    def get_media_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Media]:
        return self.db.query(Media).filter(Media.user_id == user_id).offset(skip).limit(limit).all()

    def create_media(self, media: MediaUpload, user_id: uuid.UUID) -> Media:
        db_media = Media(
            user_id=user_id,
            url=media.url,
            media_type=media.media_type,
            is_public=media.is_public
        )
        self.db.add(db_media)
        self.db.commit()
        self.db.refresh(db_media)
        return db_media

    def delete_media(self, media_id: uuid.UUID):
        db_media = self.db.query(Media).filter(Media.media_id == media_id).first()
        if db_media:
            self.db.delete(db_media)
            self.db.commit()
            return True
        return False # Indicate if not found