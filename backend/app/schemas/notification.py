from datetime import datetime
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):

    user_id: int
    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)
    notification_type: str = Field(min_length=1, max_length=50)


class NotificationUpdate(BaseModel):

    is_read: bool


class NotificationResponse(BaseModel):
    
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}