from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.model_database.promotions.coupon import Coupon
from app.model_database.users.user import User
from app.schemas.coupon import (
    CouponCreate, 
    CouponResponse,
    CouponUpdate,
    CouponUpdateStatus,

)

from app.core.security import require_role

admin = APIRouter(prefix="/admin/coupons", tags=["Coupons Management"])


# ADMIN ==========================
# CREATE COUPON
@admin.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to create coupon")

    return new_coupon


# GET ALL CODING
@admin.get("", response_model=list[CouponResponse])
async def get_coupons(db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(require_role("ADMIN"))
                      ):

    query = select(Coupon).order_by(Coupon.id.desc())

    result = await db.execute(query)

    coupons = result.scalars().all()

    return coupons


# GET CODING ID
@admin.get("/{coupon_id}", response_model=CouponResponse)
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
@admin.patch("/{coupon_id}", response_model=CouponResponse)
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update info coupon") 

    return coupon


# UPDATE COUPON STATUS
@admin.patch("/{coupon_id}/status", response_model=CouponResponse)
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update status coupon")

    return coupon