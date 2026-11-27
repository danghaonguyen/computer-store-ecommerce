from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.users.user import User
from app.model_database.notifications.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse


admin = APIRouter(prefix="/admin/notifications", tags=["Notifications Management"])


# GET ALL NOTIFICATIONS
@admin.get("", response_model=list[NotificationResponse])
async def get_all_notifications(db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query = select(Notification).order_by(Notification.created_at.desc())

    result = await db.execute(query)

    all_notifications = result.scalars().all()

    return all_notifications



# CREATE NOTIFICATION
@admin.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(notification_data: NotificationCreate,
                              db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    query = select(User).where(User.id == notification_data.user_id)

    result = await db.execute(query)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    new_notification = Notification(**notification_data.model_dump())

    try:
        db.add(new_notification)
        await db.commit()
        await db.refresh(new_notification)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create notification")

    return new_notification


# DELETE NOTIFICATION
@admin.delete("/{notification_id}", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    query = select(Notification).where(Notification.id == notification_id)

    result = await db.execute(query)

    notification = result.scalar_one_or_none()

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Notification not found")

    try:
        await db.delete(notification)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to delete notification")

    return {"message" : "Notification deleted successfully"}