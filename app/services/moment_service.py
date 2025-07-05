from sqlalchemy.orm import Session
from app.models.moment import Moment
from app.models.media import Media
from app.schemas.moment import MomentCreate, MomentUpdate
from typing import List, Optional
import uuid

class MomentService:
    def __init__(self, db: Session):
        self.db = db

    def get_moment(self, moment_id: uuid.UUID) -> Optional[Moment]:
        return self.db.query(Moment).filter(Moment.moment_id == moment_id).first()
    
    def create_moment(self, moment_data: MomentCreate) -> Moment:
        new_moment = Moment(**moment_data.model_dump())
        self.db.add(new_moment)
        self.db.commit()
        self.db.refresh(new_moment)
        return new_moment
    
    def update_moment(self, moment_id: uuid.UUID, moment_data: MomentUpdate) -> Optional[Moment]:
        moment = self.get_moment(moment_id)
        if not moment:
            return None
        
        for key, value in moment_data.model_dump(exclude_unset=True).items():
            setattr(moment, key, value)
        
        self.db.commit()
        self.db.refresh(moment)
        return moment
    
    def delete_moment(self, moment_id: uuid.UUID) -> bool:
        moment = self.get_moment(moment_id)
        if not moment:
            return False
        
        # Delete associated media
        self.db.query(Media).filter(Media.moment_id == moment_id).delete()
        
        # Delete the moment itself
        self.db.delete(moment)
        self.db.commit()
        return True
    
    def get_user_moments(self, user_id: uuid.UUID) -> List[Moment]:
        return self.db.query(Moment).filter(Moment.user_id == user_id).all()
    
    def get_public_moments(self) -> List[Moment]:
        return self.db.query(Moment).filter(Moment.is_public == True).all()
    
    def get_moments_by_ids(self, moment_ids: List[uuid.UUID]) -> List[Moment]:
        return self.db.query(Moment).filter(Moment.moment_id.in_(moment_ids)).all()
    
    def get_moment_by_slug(self, slug: str) -> Optional[Moment]:
        return self.db.query(Moment).filter(Moment.slug == slug).first()