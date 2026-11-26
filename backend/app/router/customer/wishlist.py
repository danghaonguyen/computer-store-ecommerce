from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.core.security import require_role
from app.model_database.users.user import User
from app.model_database.carts.wishlist import Wishlist
from app.model_database.products.product_variant import ProductVariant
from app.schemas.wishlist import WishlistCreate, WishlistResponse


customer = APIRouter(prefix="/wishlist", tags=["Wishlist - Customer"])


# GET WISHLIST
@customer.get("", response_model=list[WishlistResponse])
async def get_wishlist(db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("CUSTOMER"))
                       ):

    query = select(Wishlist).options(

        selectinload(Wishlist.product_variant)

    ).where(Wishlist.user_id == current_user.id)

    result = await db.execute(query)

    wishlists = result.scalars().all()

    return wishlists


# ADD PRODUCT IN WISHLIST
@customer.post("", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_product_wishlist(wishlist_data: WishlistCreate,
                               db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(require_role("CUSTOMER"))
                               ):

    query = select(Wishlist).options(

        selectinload(Wishlist.product_variant)

    ).where(Wishlist.user_id == current_user.id,
            Wishlist.product_variant_id == wishlist_data.product_variant_id)

    result = await db.execute(query)

    wishlist = result.scalar_one_or_none()

    if wishlist is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Product variant already exists in wishlist")

    query = select(ProductVariant).options(

        selectinload(ProductVariant.product)

    ).where(ProductVariant.id == wishlist_data.product_variant_id)

    result = await db.execute(query)

    variant = result.scalar_one_or_none()

    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product variant not found")

    if not variant.is_active or not variant.product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product variant is not available")

    wishlist = Wishlist(user_id=current_user.id,
                        product_variant_id=variant.id)


    try:
        db.add(wishlist)
        await db.commit()

        query = select(Wishlist).options(

            selectinload(Wishlist.product_variant)

        ).where(Wishlist.id == wishlist.id)

        result = await db.execute(query)

        wishlist = result.scalar_one()

    except Exception:
        await db.rollback()
        raise


    return wishlist


# DELETE PRODUCT IN WISHLIST
@customer.delete("/{wishlist_id}")
async def delete_product_wishlist(wishlist_id: int,
                                  db: AsyncSession = Depends(get_db),
                                  current_user: User = Depends(require_role("CUSTOMER"))
                                  ):

    query = select(Wishlist).where(Wishlist.id == wishlist_id, 
                                   Wishlist.user_id == current_user.id)

    result = await db.execute(query)

    wishlist = result.scalar_one_or_none()

    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Wishlist not found")

    try:
        await db.delete(wishlist)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {"message" : "Wishlist deleted successfully"}