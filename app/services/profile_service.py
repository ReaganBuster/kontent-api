from sqlalchemy.orm import Session
from typing import Optional
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
import uuid

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, profile_id: uuid.UUID) -> Optional[ProfileResponse]:
        return self.db.query(Profile).filter(Profile.profile_id == profile_id).first()

    def create_profile(self, profile_data: ProfileCreate, user_id: uuid.UUID) -> ProfileResponse:
        new_profile = Profile(**profile_data.model_dump(), user_id=user_id)
        self.db.add(new_profile)
        self.db.commit()
        self.db.refresh(new_profile)
        return ProfileResponse.model_validate(new_profile)

    def update_profile(self, profile_id: uuid.UUID, profile_data: ProfileUpdate) -> Optional[ProfileResponse]:
        profile = self.get_profile(profile_id)
        if not profile:
            return None
        
        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return ProfileResponse.model_validate(profile)