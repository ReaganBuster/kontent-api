
from fastapi import HTTPException, status
from app.models.flirt import Flirt
from app.schemas.flirt import FlirtCreate, FlirtResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.models.moment import Moment

class FlirtService:
    def __init__(self, db: Session):
        self.db = db

    def get_flirt(self, flirt_id: uuid.UUID) -> Optional[Flirt]:
        return self.db.query(Flirt).filter(Flirt.flirt_id == flirt_id).first()

    def get_flirts_by_moment(self, moment_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Flirt]:
        return self.db.query(Flirt).filter(Flirt.moment_id == moment_id).offset(skip).limit(limit).all()

    def get_flirts_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Flirt]:
        return self.db.query(Flirt).filter(Flirt.flirter_id == user_id).offset(skip).limit(limit).all()

    def create_flirt(self, flirter_id: uuid.UUID, moment_id: uuid.UUID) -> Flirt:
        # Check for existing flirt to enforce unique constraint
        existing_flirt = self.db.query(Flirt).filter(
            Flirt.flirter_id == flirter_id,
            Flirt.moment_id == moment_id
        ).first()
        if existing_flirt:
            return existing_flirt # Return existing if already flirted

        db_flirt = Flirt(
            flirter_id=flirter_id,
            moment_id=moment_id
        )
        self.db.add(db_flirt)
        self.db.commit()
        self.db.refresh(db_flirt)

        # Increment flirt_count on the Moment
        moment = self.db.query(Moment).filter(Moment.moment_id == moment_id).first()
        if moment:
            moment.flirt_count += 1
            self.db.add(moment)
            self.db.commit()
            self.db.refresh(moment)

        return db_flirt

    def delete_flirt(self, flirt_id: uuid.UUID) -> bool:
        db_flirt = self.db.query(Flirt).filter(Flirt.flirt_id == flirt_id).first()
        if db_flirt:
            # Decrement flirt_count on the Moment
            moment = self.db.query(Moment).filter(Moment.moment_id == db_flirt.moment_id).first()
            if moment and moment.flirt_count > 0:
                moment.flirt_count -= 1
                self.db.add(moment)
                self.db.commit()
                self.db.refresh(moment)

            self.db.delete(db_flirt)
            self.db.commit()
            return True
        return False