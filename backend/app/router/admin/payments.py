from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.core.security import require_role

from app.model_database.users.user import User
from app.model_database.payments.payment import Payment

from app.schemas.payment import (
    PaymentDetailResponse,
    PaymentResponse
)

admin = APIRouter(prefix="/admin/payments", tags=["Payments - Admin"])

# ADMIN ========================================
# GET PAYMENT LIST
@admin.get("",response_model=list[PaymentResponse])
async def get_payments(payment_status: str | None = None, 
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(require_role("ADMIN"))
                       ):
    
    query = select(Payment).order_by(desc(Payment.created_at))

    if payment_status:
        query = query.where(
            Payment.payment_status == payment_status.upper()
        )

    result = await db.execute(query)
    payments = result.scalars().all()

    return payments


# GET PAYMENT DETAIL
@admin.get("/{payment_id}",response_model=PaymentDetailResponse)
async def get_payment_detail(payment_id: int, db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(require_role("ADMIN"))
                             ):
    
    query = (
        select(Payment)
        .options(selectinload(Payment.transactions))
        .where(Payment.id == payment_id)
    )

    result = await db.execute(query)
    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment
