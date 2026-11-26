from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.model_database.promotions.coupon import Coupon
from app.model_database.promotions.coupon_usage import CouponUsage
from app.model_database.users.user import User
from app.schemas.coupon import (
    CouponValidate,
    CouponValidateResponse
)

from app.core.security import require_role
from datetime import datetime, timezone
from decimal import Decimal


customer = APIRouter(prefix="/coupons", tags=["Coupons - Customer"])

# CUSTOMER ==========================
# VALIDATE COUPON
@customer.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(coupon_data: CouponValidate,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("CUSTOMER"))
                          ):

    # Find coupon
    query = select(Coupon).where(Coupon.code == coupon_data.code)

    result = await db.execute(query)

    coupon = result.scalar_one_or_none()

    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Coupon not found")

    # Check status coupon
    if not coupon.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Coupon is inactive")

    # Check coupon time
    now = datetime.now(timezone.utc)

    if now < coupon.start_at or now > coupon.end_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Coupon is not available at this time")


    # Check minium order amount
    if coupon_data.subtotal < coupon.minimum_order_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Order amount does not meet coupon minium")


    # Check total usage limit
    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Coupon usage limit exceeded")


    # Check user usage limit
    query = select(func.count(CouponUsage.id)).where(

        CouponUsage.coupon_id == coupon.id,
        CouponUsage.user_id == current_user.id

    )

    result = await db.execute(query)

    user_used_count = result.scalar_one()

    if user_used_count >= coupon.usage_limit_per_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have exceeded the coupon usage limit")


    # Calculate discount
    if coupon.discount_type == "PERCENTAGE":
        discount_amount = coupon_data.subtotal * coupon.discount_value / Decimal("100")

        # Apply maxium discount limit:
        if coupon.maximum_discount_amount is not None:
            discount_amount = min(discount_amount, coupon.maximum_discount_amount)


    else:
        discount_amount = coupon.discount_value

    # Discount cannot exceed subtotal
    discount_amount = min(discount_amount, coupon_data.subtotal)

    # Calculate total after discount
    total_after_discount = coupon_data.subtotal - discount_amount

    response_coupon = CouponValidateResponse(

        code=coupon.code,
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
        subtotal=coupon_data.subtotal,
        discount_amount=discount_amount,
        total_after_discount=total_after_discount
    )

    return response_coupon