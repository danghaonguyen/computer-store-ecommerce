from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.core.security import require_role
from app.model_database.users.user import User
from app.model_database.carts.cart import Cart
from app.model_database.products.product_variant import ProductVariant
from app.model_database.carts.cart_item import CartItem
from app.schemas.cart import (
    CartResponse, 
    CartItemCreate, 
    CartItemUpdate,
    CartItemResponse
)

customer = APIRouter(prefix="/cart", tags=["Carts - Customer"])


# GET CART
@customer.get("", response_model=CartResponse)
async def get_cart(db: AsyncSession = Depends(get_db), 
                   current_user: User = Depends(require_role("CUSTOMER"))
                   ):

    query = select(Cart).options(

        selectinload(Cart.items).selectinload(CartItem.product_variant)

    ).where(Cart.user_id == current_user.id)

    result = await db.execute(query)

    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=current_user.id)

        try:
            db.add(cart)
            await db.commit()

            result = await db.execute(query)
            cart = result.scalar_one()

        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail="Failed to get cart")

    return cart

# ADD CART ITEM IN CART
@customer.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(item_data: CartItemCreate, 
                        db: AsyncSession = Depends(get_db), 
                        current_user: User = Depends(require_role("CUSTOMER"))
                        ):

    query = select(ProductVariant).options(

        selectinload(ProductVariant.product)

    ).where(ProductVariant.id == item_data.product_variant_id)

    result = await db.execute(query)

    variant = result.scalar_one_or_none()

    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product variant not found")

    if not variant.is_active or not variant.product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Product variant is not available")


    query = select(Cart).where(Cart.user_id == current_user.id)

    result = await db.execute(query)

    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=current_user.id)

        db.add(cart)

        await db.flush()

    query = select(CartItem).where(

        CartItem.cart_id == cart.id,
        CartItem.product_variant_id == variant.id
    )

    result = await db.execute(query)

    cart_item = result.scalar_one_or_none()

    if cart_item is not None:
        cart_item.quantity += item_data.quantity

    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_variant_id=variant.id,
            quantity=item_data.quantity
        )

    try:
        db.add(cart_item)
        await db.commit()

        query = select(Cart).options(

            selectinload(Cart.items).selectinload(CartItem.product_variant)

        ).where(Cart.id == cart.id)

        result = await db.execute(query)

        cart = result.scalar_one()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to create cart item")

    return cart

# UPDATE QUANTITY CART ITEM
@customer.patch("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(item_id: int, item_data: CartItemUpdate, 
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("CUSTOMER"))
                           ):

    query = select(CartItem).options(

        selectinload(CartItem.product_variant)

        ).join(Cart).where(CartItem.id == item_id,
                                   Cart.user_id == current_user.id)

    result = await db.execute(query)

    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cart item not found")

    cart_item.quantity = item_data.quantity

    try:
        await db.commit()
        await db.refresh(cart_item)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to update quantity cart items")

    return cart_item


# DELETE CART ITEM
@customer.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_cart_item(item_id: int,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("CUSTOMER"))
                           ):

    query = select(CartItem).join(Cart).where(CartItem.id == item_id,
                                              Cart.user_id == current_user.id)


    result = await db.execute(query)

    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Cart item not found")

    try:
        await db.delete(cart_item)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to deletd cart item")

    return {"message": "Cart item deleted successfully"}