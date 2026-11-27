from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.core.security import require_role
from app.model_database.users.user import User
from app.model_database.products.product import Product
from app.model_database.products.category import Category
from app.model_database.products.brand import Brand
from app.model_database.reviews.review import Review
from app.schemas.product import ProductCreate, ProductResponse, ProductStatusUpdate, ProductUpdate


admin = APIRouter(prefix="/admin/products", tags=["Products Management"])

# CREATE PRODUCT
@admin.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, 
                         db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(require_role("ADMIN"))
                         ):

    query = select(Product).where(Product.slug == product_data.slug)

    result = await db.execute(query)

    product_slug = result.scalar_one_or_none()

    if product_slug:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Product slug already exists")


    query = select(Category).where(Category.id == product_data.category_id)

    result = await db.execute(query)

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Category not found")

    query = select(Brand).where(Brand.id == product_data.brand_id)

    result = await db.execute(query)

    brand = result.scalar_one_or_none()

    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Brand not found")

    new_product = Product(**product_data.model_dump())

    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to create product")

    return new_product


# GET PRODUCT
@admin.get("", response_model=list[ProductResponse])
async def get_product(db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_role("ADMIN"))
                      ):

    query = select(Product)

    result = await db.execute(query)

    product = result.scalars().all()

    return product


# GET PRODUCT ID
@admin.get("/{product_id}", response_model=ProductResponse)
async def get_product_id(product_id: int, 
                         db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(require_role("ADMIN"))
                         ):

    query = select(Product).where(Product.id == product_id)

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    return product

# UPDATE PRODUCT
@admin.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductUpdate, 
                         db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(require_role("ADMIN"))
                         ):

    query = select(Product).where(Product.id == product_id)

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    update_data = product_data.model_dump(exclude_unset=True)

    if "slug" in update_data:
        query = select(Product).where(
            Product.slug == update_data["slug"], 
            Product.id != product_id)

        result = await db.execute(query)

        existing_product = result.scalar_one_or_none()

        if existing_product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Product slug already exists")
        
    if "category_id" in update_data:
        query = select(Category).where(Category.id == update_data["category_id"])

        result = await db.execute(query)

        exists_category_id = result.scalar_one_or_none()

        if exists_category_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Category not found")

    if "brand_id" in update_data:    
        query = select(Brand).where(Brand.id == update_data["brand_id"])

        result = await db.execute(query)

        exists_brand_id = result.scalar_one_or_none()

        if exists_brand_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Brand not found")    

    for key, value in update_data.items():
        setattr(product, key, value)

    try:
        await db.commit()
        await db.refresh(product)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update info product")

    return product


# UPDATE PRODUCT STATUS
@admin.patch("/{product_id}/status", response_model=ProductResponse)
async def update_product_status(product_id: int, product_data: ProductStatusUpdate, 
                                db: AsyncSession = Depends(get_db), 
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query = select(Product).where(Product.id == product_id)

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    product.is_active = product_data.is_active

    try:
        await db.commit()
        await db.refresh(product)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update status product")

    return product


# DELETE PRODUCT
@admin.delete("/{product_id}")
async def delete_product(product_id: int, 
                         db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(require_role("ADMIN"))
                         ):

    query = select(Product).where(Product.id == product_id)

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query = select(Review).where(Review.product_id == product_id)

    result = await db.execute(query)

    review = result.scalar_one_or_none()

    if review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Cannot delete product because it has reviews")
    
    try:
        await db.delete(product)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to delete product")

    return {"message": "Product deleted successfully"}
