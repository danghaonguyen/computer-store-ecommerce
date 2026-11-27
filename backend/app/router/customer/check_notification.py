from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.notifications.notification import Notification
from app.model_database.users.user import User
from app.schemas.notification import NotificationResponse, NotificationUpdate

customer = APIRouter(prefix="/notifications", tags=["Notifications - Customer"])


# CHECK ALL NOTIFICATIONS
@customer.get("", response_model=list[NotificationResponse])
async def check_all_notifications(db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(require_role("CUSTOMER"))
                                ):

    query = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())

    result = await db.execute(query)

    notifications = result.scalars().all()

    return notifications


# MARK THIS NOTIFICATION AS READ
@customer.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(notification_id: int, db: AsyncSession = Depends(get_db),
                                    current_user: User = Depends(require_role("CUSTOMER"))
                                    ):

    query = select(Notification).where(Notification.id == notification_id,
                                       Notification.user_id == current_user.id)

    result = await db.execute(query)

    notification = result.scalar_one_or_none()

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Notification not found")

    if notification.is_read:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Notification has already been read")
    
    notification.is_read = True
    

    try:
        await db.commit()
        await db.refresh(notification)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to mark notification")

    return notification


# MARK THIS ALL NOTIFICATION AS READ
@customer.patch("/read-all", status_code=status.HTTP_200_OK)
async def mark_this_all_notification_as_read(db: AsyncSession = Depends(get_db),
                                             current_user: User = Depends(require_role("CUSTOMER"))
                                             ):

    query = select(Notification).where(Notification.user_id == current_user.id)

    result = await db.execute(query)

    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True

    try:
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to mark all notifications")

    return notifications


# DELETE NOTIFICATION
@customer.delete("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(require_role("CUSTOMER"))
                              ):

    query = select(Notification).where(Notification.id == notification_id,
                                       Notification.user_id == current_user.id)

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

