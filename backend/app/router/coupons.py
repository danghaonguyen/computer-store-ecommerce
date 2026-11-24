from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.database import get_db
from app.model_database.promotions.coupon import Coupon
from app.model_database.promotions.coupon_usage import CouponUsage
from app.model_database.users.user import User
from app.schemas.coupon import (
    CouponCreate, 
    CouponResponse,
    CouponUpdate,
    CouponUpdateStatus,
    CouponValidate,
    CouponValidateResponse
)

from app.core.security import require_role
from datetime import datetime, timezone
from decimal import Decimal


router = APIRouter(prefix="/coupons", tags=["Coupons"])


# ADMIN ==========================
@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(coupon_data: CouponCreate, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("ADMIN"))
                        ):

    # Check duplicate coupon code
    query = select(Coupon).where(Coupon.code == coupon_data.code)

    result = await db.execute(query)

    existing_coupon = result.scalar_one_or_none()

    if existing_coupon is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Coupon code already exists")


    new_coupon = Coupon(**coupon_data.model_dump())

    try:
        db.add(new_coupon)
        await db.commit()
        await db.refresh(new_coupon)

    except Exception:
        await db.rollback()
        raise

    return new_coupon


# GET ALL CODING
@router.get("", response_model=list[CouponResponse])
async def get_coupons(db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(require_role("ADMIN"))
                      ):

    query = select(Coupon).order_by(Coupon.id.desc())

    result = await db.execute(query)

    coupons = result.scalars().all()

    return coupons


# GET CODING ID
@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon_id(coupon_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("ADMIN"))
                        ):

    query = select(Coupon).where(Coupon.id == coupon_id)

    result = await db.execute(query)

    coupon = result.scalar_one_or_none()

    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Coupon not found")

    return coupon



# UPDATE COUPON
@router.patch("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(coupon_id: int, coupon_data: CouponUpdate,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("ADMIN"))
                        ):

    query = select(Coupon).where(Coupon.id == coupon_id)

    result = await db.execute(query)

    coupon = result.scalar_one_or_none()

    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Coupon not found")

    update_data = coupon_data.model_dump(exclude_unset=True)

    if "code" in update_data:

        query = select(Coupon).where(Coupon.code == update_data["code"],
                                     Coupon.id != coupon_id)

        result = await db.execute(query)

        coupon_code = result.scalar_one_or_none()

        if coupon_code is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Coupon code already exists")

    # Validate final coupon data
    discount_type = update_data.get("discount_type", coupon.discount_type)
    discount_value = update_data.get("discount_value", coupon.discount_value)

    start_at = update_data.get("start_at", coupon.start_at)
    end_at = update_data.get("end_at", coupon.end_at)

    if discount_type == "PERCENTAGE" and discount_value > 100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Percentage discount cannot excced 100")

    if end_at <= start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="End date must be after start date")

    for key, value in update_data.items():
        setattr(coupon, key, value)

    try:
        await db.commit()
        await db.refresh(coupon)

    except Exception:
        await db.rollback()
        raise 

    return coupon


# UPDATE COUPON STATUS
@router.patch("/{coupon_id}/status", response_model=CouponResponse)
async def update_coupon_status(coupon_id: int, coupon_data: CouponUpdateStatus,
                               db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(require_role("ADMIN"))
                               ):

    query = select(Coupon).where(Coupon.id == coupon_id)

    result = await db.execute(query)

    coupon = result.scalar_one_or_none()

    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Coupon not found")

    coupon.is_active = coupon_data.is_active

    try:
        await db.commit()
        await db.refresh(coupon)

    except Exception:
        await db.rollback()
        raise

    return coupon


# CUSTOMER ==========================
# VALIDATE COUPON
@router.post("/validate", response_model=CouponValidateResponse)
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