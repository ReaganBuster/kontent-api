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
    
    def create_moment(self, moment_data: MomentCreate, user_id: uuid.UUID) -> Moment:
        # 1. Unpack only the relevant fields for the Moment model
        new_moment = Moment(
            user_id=user_id,
            text_content=moment_data.text_content,
            visibility=moment_data.visibility
        )

        self.db.add(new_moment)
        self.db.flush()  # This assigns new_moment.moment_id without committing yet

        # 2. Associate media (if any)
        if moment_data.media_ids:
            media_items = self.db.query(Media).filter(Media.media_id.in_(moment_data.media_ids)).all()
            for media in media_items:
                media.moment_id = new_moment.moment_id
                self.db.add(media)  # Optional, since already in session

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
        return self.db.query(Moment).filter().all()
    
    def get_moments_by_ids(self, moment_ids: List[uuid.UUID]) -> List[Moment]:
        return self.db.query(Moment).filter(Moment.moment_id.in_(moment_ids)).all()
    
    def get_moment_by_slug(self, slug: str) -> Optional[Moment]:
        return self.db.query(Moment).filter(Moment.slug == slug).first()