from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.moment import MomentCreate, MomentUpdate, MomentResponse
from app.services.moment_service import MomentService
from app.services.user_service import UserService as crud_user

router = APIRouter()

@router.post("/", response_model=MomentResponse, status_code=status.HTTP_201_CREATED)
def create_moment(moment: MomentCreate, current_user: crud_user.get_user = Depends(get_current_user), db: Session = Depends(get_db)):
    crud_moment = MomentService(db)
    # You would also handle media uploads here, linking them to the moment after they are uploaded
    db_moment = crud_moment.create_moment(moment_data=moment, user_id=current_user.user_id)
    # Load author relationship for the response model
    db_moment.author # Accessing the relationship to load it for Pydantic
    db_moment.media # Accessing media to load it
    return db_moment

@router.get("/", response_model=List[MomentResponse])
def read_all_moments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crud_moment = MomentService(db)
    # In a real app, this would be a feed, potentially filtered, paginated, and personalized
    moments = crud_moment.get_public_moments()
    # Eagerly load relationships to avoid N+1 queries if you're returning many moments
    # moments = db.query(Moment).options(joinedload(Moment.author), joinedload(Moment.media)).offset(skip).limit(limit).all()
    return moments

@router.get("/{moment_id}", response_model=MomentResponse)
def read_moment(moment_id: uuid.UUID, db: Session = Depends(get_db)):
    crud_moment = MomentService(db)
    
    moment = crud_moment.get_moment(moment_id=moment_id)
    if not moment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
    # Increment views (optional, could be async or batched)
    moment.views += 1
    db.add(moment)
    db.commit()
    db.refresh(moment)
    return moment

@router.put("/{moment_id}", response_model=MomentResponse)
def update_moment(
    moment_id: uuid.UUID,
    moment_in: MomentUpdate,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud_moment = MomentService(db)
    db_moment = crud_moment.get_moment( moment_id=moment_id)
    if not db_moment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
    if db_moment.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this moment")
    
    updated_moment = crud_moment.update_moment( moment_id=moment_id, moment_data=moment_in)
    return updated_moment

@router.delete("/{moment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_moment(
    moment_id: uuid.UUID,
    current_user: crud_user.get_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud_moment = MomentService(db)
    db_moment = crud_moment.get_moment( moment_id=moment_id)
    if not db_moment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
    if db_moment.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this moment")
    
    crud_moment.delete_moment( moment_id=moment_id)
    return