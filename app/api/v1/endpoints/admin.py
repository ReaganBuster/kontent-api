from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.monetisation import MonetizationConfigBase, MonetizationConfigResponse
from app.services.monetisation_config_service import MonetisationConfigService as crud_monetization_config
from app.services.user_service import UserService as crud_user

router = APIRouter()

# A simple admin check - in a real app, use roles in JWT claims
def get_current_admin_user(current_user: crud_user.get_user = Depends(get_current_user)):
    # This is a placeholder. You need real role-based authorization here.
    # E.g., if "admin" not in current_user.roles:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
    return current_user

@router.post("/monetization_configs", response_model=MonetizationConfigResponse, status_code=status.HTTP_201_CREATED)
def create_monetization_config(
    config_in: MonetizationConfigBase,
    admin_user: crud_user.get_user = Depends(get_current_admin_user), # Only admins can create
    db: Session = Depends(get_db)
):
    """Create a new monetization configuration."""
    return crud_monetization_config.create_monetization_config(db, config_in=config_in)

@router.get("/monetization_configs", response_model=List[MonetizationConfigResponse])
def get_all_monetization_configs(
    admin_user: crud_user.get_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Retrieve all monetization configurations (admin only)."""
    return db.query(crud_monetization_config.MonetizationConfig).all()

@router.get("/monetization_configs/active", response_model=List[MonetizationConfigResponse])
def get_active_monetization_configs_public(
    db: Session = Depends(get_db)
):
    """Retrieve active monetization configurations (can be public for client-side display of fees)."""
    return crud_monetization_config.get_active_monetization_configs(db)


@router.put("/monetization_configs/{config_id}", response_model=MonetizationConfigResponse)
def update_monetization_config(
    config_id: uuid.UUID,
    config_in: MonetizationConfigBase, # Use Base as input for updates
    admin_user: crud_user.get_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update an existing monetization configuration."""
    db_config = crud_monetization_config.get_monetization_config(db, config_id=config_id)
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monetization config not found")
    
    return crud_monetization_config.update_monetization_config(db, db_config=db_config, config_in=config_in)

@router.put("/monetization_configs/{config_id}/deactivate", response_model=MonetizationConfigResponse)
def deactivate_monetization_config(
    config_id: uuid.UUID,
    admin_user: crud_user.get_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a monetization configuration."""
    db_config = crud_monetization_config.deactivate_monetization_config(db, config_id=config_id)
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monetization config not found")
    return db_config