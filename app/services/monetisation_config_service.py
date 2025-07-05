from sqlalchemy.orm import Session
from app.models.monetisation_config import MonetizationConfig
from app.schemas.monetisation import MonetizationConfigBase, MonetizationConfigResponse
from typing import List, Optional
import uuid

class MonetisationConfigService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_monetization_config(self, config_id: uuid.UUID) -> Optional[MonetizationConfig]:
        return self.db.query(MonetizationConfig).filter(MonetizationConfig.config_id == config_id).first()

    def get_monetization_config_by_name(self, name: str) -> Optional[MonetizationConfig]:
        return self.db.query(MonetizationConfig).filter(MonetizationConfig.config_name == name).first()

    def get_active_monetization_configs(self) -> List[MonetizationConfig]:
        return self.db.query(MonetizationConfig).filter(MonetizationConfig.is_active == True).all()

    def create_monetization_config(self, config_in: MonetizationConfigBase) -> MonetizationConfig:
        db_config = MonetizationConfig(**config_in.model_dump())
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def update_monetization_config(self, db_config: MonetizationConfig, config_in: MonetizationConfigBase) -> MonetizationConfig:
        update_data = config_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def deactivate_monetization_config(self, config_id: uuid.UUID) -> Optional[MonetizationConfig]:
        db_config = self.db.query(MonetizationConfig).filter(MonetizationConfig.config_id == config_id).first()
        if db_config:
            db_config.is_active = False
            self.db.add(db_config)
            self.db.commit()
            self.db.refresh(db_config)
            return db_config
        return None