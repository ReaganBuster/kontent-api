import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def test_create_user(db):
    user_service = UserService(db)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123"
    )
    
    user = user_service.create_user(user_data)
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True

def test_get_user_by_email(db):
    user_service = UserService(db)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123"
    )
    
    created_user = user_service.create_user(user_data)
    found_user = user_service.get_user_by_email("test@example.com")
    
    assert found_user.id == created_user.id
    assert found_user.email == "test@example.com"
