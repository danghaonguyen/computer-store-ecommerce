from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.products.product_image import ProductImage
from app.model_database.products.product import Product
from app.model_database.users.user import User
from app.schemas.product_image import (
    ProductImageCreate, 
    ProductImageResponse,
    ProductImageUpdate
)

router = APIRouter(prefix="/products/{product_id}/images", tags=["Product Images"])


# ADD PRODUCT IMAGES
@router.post("", response_model=ProductImageResponse)
async def create_product_image(
    product_id: int,
    image_data: ProductImageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    try:
        if image_data.is_primary:
            query_images = select(ProductImage).where(
                ProductImage.product_id == product_id, ProductImage.is_primary == True
            )

            result_images = await db.execute(query_images)

            existing_images = result_images.scalars().all()

            for image in existing_images:
                image.is_primary = False

        new_image = ProductImage(product_id=product_id, **image_data.model_dump())

        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)

    except Exception:
        await db.rollback()
        raise

    return new_image


# GET PRODUCT IMAGES
@router.get("", response_model=list[ProductImageResponse])
async def get_product_images(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    query_images = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
    )

    result_images = await db.execute(query_images)
    images = result_images.scalars().all()

    return images

# GET PRODUCT IMAGES ID
@router.get("/{image_id}", response_model=ProductImageResponse)
async def get_product_images_id(product_id: int, image_id: int, 
                                db: AsyncSession = Depends(get_db), 
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_image = select(ProductImage).where(ProductImage.id == image_id, 
                                             ProductImage.product_id == product_id)

    result_image = await db.execute(query_image)

    image = result_image.scalar_one_or_none()

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product image not found")

    return image


# UPDATE PRODUCT IMAGES
@router.patch("/{image_id}", response_model=ProductImageResponse)
async def update_product_image(product_id: int, image_id: int, 
                               image_data: ProductImageUpdate, 
                               db: AsyncSession = Depends(get_db), 
                               current_user: User = Depends(require_role("ADMIN"))
                               ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_image = select(ProductImage).where(ProductImage.id == image_id, 
                                             ProductImage.product_id == product_id)

    result_image = await db.execute(query_image)

    image = result_image.scalar_one_or_none()

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product image not found")

    update_data = image_data.model_dump(exclude_unset=True)

    try:
        if update_data.get("is_primary") is True:
            query_images = select(ProductImage).where(ProductImage.product_id == product_id, 
                                                      ProductImage.is_primary == True, 
                                                      ProductImage.id != image_id)

            result_image = await db.execute(query_images)

            existing_images = result_image.scalars().all()

            for existing_image in existing_images:
                existing_image.is_primary = False


        for key, value in update_data.items():
            setattr(image, key, value)

        await db.commit()
        await db.refresh(image)

    except Exception:
        await db.rollback()
        raise

    return image


# DELETE PRODUCT IMAGES
@router.delete("/{image_id}")
async def delete_product_image(product_id: int, image_id: int, 
                               db: AsyncSession = Depends(get_db), 
                               current_user: User = Depends(require_role("ADMIN"))
                               ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_image = select(ProductImage).where(ProductImage.id == image_id, 
                                             ProductImage.product_id == product_id)

    result_image = await db.execute(query_image)

    image = result_image.scalar_one_or_none()

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product image not found")

    try:
        await db.delete(image)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {"message" : "Product Image deleted successfully"}

    