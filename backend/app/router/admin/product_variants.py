from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.security import require_role
from app.model_database.products.product import Product
from app.model_database.products.product_variant import ProductVariant
from app.model_database.carts.cart_item import CartItem
from app.model_database.inventory.inventory import Inventory
from app.model_database.orders.order_item import OrderItem
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
    ProductVariantStatusUpdate
)
from app.model_database.users.user import User

admin = APIRouter(prefix="/admin/products/{product_id}/variants", 
                   tags=["Product Variants Management"])

# ADD PRODUCT VARIANT
@admin.post("", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
async def create_product_variant(product_id: int, variant_data: ProductVariantCreate, 
                                 db: AsyncSession = Depends(get_db), 
                                 current_user: User = Depends(require_role("ADMIN"))
                                 ):
    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_sku = select(ProductVariant).where(ProductVariant.sku == variant_data.sku)

    result_sku = await db.execute(query_sku)

    existing_variant = result_sku.scalar_one_or_none()

    if existing_variant:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="SKU already exists")

    new_variant = ProductVariant(product_id=product_id, 
                                 **variant_data.model_dump())

    try:
        db.add(new_variant)
        await db.commit()
        await db.refresh(new_variant)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to create product variant")

    return new_variant


# GET PRODUCT VARIANT
@admin.get("", response_model=list[ProductVariantResponse])
async def get_product_variant(product_id: int, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_variant = select(ProductVariant).where(ProductVariant.product_id == product_id)

    result_variant = await db.execute(query_variant)
    variant = result_variant.scalars().all()

    return variant


# GET PRODUCT VARIANT ID
@admin.get("/{variant_id}", response_model=ProductVariantResponse)
async def get_product_variant_id(product_id: int, variant_id: int, 
                                 db: AsyncSession = Depends(get_db), 
                                 current_user: User = Depends(require_role("ADMIN"))
                                 ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_variant = select(ProductVariant).where(ProductVariant.id == variant_id, 
                                                 ProductVariant.product_id == product_id)

    result_variant = await db.execute(query_variant)
    variant = result_variant.scalar_one_or_none()

    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product variant not found")

    return variant

# UPDATE PRODUCT VARIANT ID
@admin.patch("/{variant_id}", response_model=ProductVariantResponse)
async def update_product_variant(product_id: int, variant_id: int, 
                                    variant_data: ProductVariantUpdate,  
                                    db: AsyncSession = Depends(get_db), 
                                    current_user: User = Depends(require_role("ADMIN"))
                                    ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_variant = select(ProductVariant).where(ProductVariant.id == variant_id, 
                                                 ProductVariant.product_id == product_id)

    result_variant = await db.execute(query_variant)

    variant = result_variant.scalar_one_or_none()

    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product variant not found")

    update_data = variant_data.model_dump(exclude_unset=True)

    if "sku" in update_data:
        query_sku = select(ProductVariant).where(ProductVariant.sku == update_data["sku"], 
                                                 ProductVariant.id != variant_id)

        result_sku = await db.execute(query_sku)

        existing_variant = result_sku.scalar_one_or_none()

        if existing_variant:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="SKU already exists")

    for key, value in update_data.items():
        setattr(variant, key, value)

    try:
        await db.commit()
        await db.refresh(variant)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update info product variant")

    return variant


# UPDATE PRODUCT VARIANT STATUS
@admin.patch("/{variant_id}/status", response_model=ProductVariantResponse)
async def update_product_variant_status(product_id: int, variant_id: int, 
                                        status_data: ProductVariantStatusUpdate, 
                                        db: AsyncSession = Depends(get_db), 
                                        current_user: User = Depends(require_role("ADMIN"))
                                        ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_variant = select(ProductVariant).where(ProductVariant.id == variant_id, 
                                                 ProductVariant.product_id == product_id)

    result_variant = await db.execute(query_variant)
    variant = result_variant.scalar_one_or_none()

    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product variant not found")

    variant.is_active = status_data.is_active

    try:
        await db.commit()
        await db.refresh(variant)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update status product variant")

    return variant


# DELETE PRODUCT VARIANT
@admin.delete("/{variant_id}")
async def delete_product_variant(product_id: int, variant_id: int, 
                                 db: AsyncSession = Depends(get_db), 
                                 current_user: User = Depends(require_role("ADMIN"))
                                 ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_variant = select(ProductVariant).where(ProductVariant.id == variant_id, 
                                                 ProductVariant.product_id == product_id)

    result_variant = await db.execute(query_variant)

    variant = result_variant.scalar_one_or_none()

    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product variant not found")

    query_cart = select(CartItem).where(CartItem.product_variant_id == variant_id)

    result_cart = await db.execute(query_cart)

    if result_cart.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Cannot delete variant because it is used in cart items")

    query_invetory = select(Inventory).where(Inventory.product_variant_id == variant_id)

    result_inventory = await db.execute(query_invetory)

    if result_inventory.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Cannot delete variant because it has inventory records")


    query_order = select(OrderItem).where(OrderItem.product_variant_id == variant_id)
    
    result_order = await db.execute(query_order)

    if result_order.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Cannot delete variant because it is used in orders")

    try: 
        await db.delete(variant)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to delete product variant")

    return {"message": "Product variant deleted successfully"}