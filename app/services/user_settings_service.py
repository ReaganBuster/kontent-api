from sqlalchemy.orm import Session
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsBase, UserSettingsUpdate
from typing import Optional
import uuid

class UserSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_settings(self, user_id: uuid.UUID) -> Optional[UserSettings]:
        return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    def create_user_settings(self, user_id: uuid.UUID, settings: UserSettingsBase) -> UserSettings:
        db_settings = UserSettings(
            user_id=user_id,
            **settings.dict()
        )
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings

    def update_user_settings(self, user_id: uuid.UUID, settings_update: UserSettingsUpdate) -> Optional[UserSettings]:
        db_settings = self.get_user_settings(user_id)
        if not db_settings:
            return None
        
        for key, value in settings_update.dict(exclude_unset=True).items():
            setattr(db_settings, key, value)
        
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings