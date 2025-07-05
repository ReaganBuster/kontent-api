from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, moments, connections, media, flirts, messages, transactions, earnings, user_settings, notifications, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(moments.router, prefix="/moments", tags=["moments"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(flirts.router, prefix="/flirts", tags=["flirts"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(earnings.router, prefix="/earnings", tags=["earnings"])
api_router.include_router(user_settings.router, prefix="/settings", tags=["user settings"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
