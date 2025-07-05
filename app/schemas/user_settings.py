from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

# Assuming ORMConfig from previous response
ORMConfig = ConfigDict(from_attributes=True)

# --- 11. UserSettings Schemas ---
class UserSettingsBase(BaseModel):
    # Notification preferences
    email_notifications_enabled: Optional[bool] = True
    push_notifications_enabled: Optional[bool] = True
    notify_new_flirt: Optional[bool] = True
    notify_connection_request: Optional[bool] = True
    notify_connection_accepted: Optional[bool] = True
    notify_new_message: Optional[bool] = True
    notify_earning_paid: Optional[bool] = True
    
    # Privacy settings
    show_online_status: Optional[bool] = True
    allow_dm_from_unconnected: Optional[bool] = False # Explicitly false by default
    discoverable: Optional[bool] = True
    
    # Display preferences
    theme_preference: Optional[str] = Field("light", pattern="^(light|dark)$")

class UserSettingsUpdate(UserSettingsBase):
    # All fields are optional for partial updates
    pass

class UserSettingsResponse(UserSettingsBase):
    settings_id: uuid.UUID
    user_id: uuid.UUID
    updated_at: datetime

    model_config = ORMConfig
