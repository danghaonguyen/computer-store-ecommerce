from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.core.security import require_role
from app.model_database.products.product import Product
from app.model_database.products.product_attribute import ProductAttribute
from app.model_database.users.user import User
from app.schemas.product_attribute import (
    ProductAttributeCreate,
    ProductAttributeResponse,
    ProductAttributeUpdate
)

router = APIRouter(prefix="/products/{product_id}/attributes", 
                   tags=["Product Attributes"])


# ADD PRODUCT ATTRIBUTES
@router.post("", response_model=ProductAttributeResponse)
async def create_product_attribute(product_id: int, attribute_data: ProductAttributeCreate, 
                                   db: AsyncSession = Depends(get_db), 
                                   current_user: User = Depends(require_role("ADMIN"))
                                   ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_attribute = select(ProductAttribute).where(ProductAttribute.product_id == product_id, 
                                                     ProductAttribute.attribute_name == attribute_data.attribute_name)

    result_attribute = await db.execute(query_attribute)

    attribute = result_attribute.scalar_one_or_none()

    if attribute is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            details="Product attribute already exists")

    try:
        new_attribute = ProductAttribute(product_id=product_id, **attribute_data.model_dump())

        db.add(new_attribute)
        await db.commit()
        await db.refresh(new_attribute)

    except Exception:
        await db.rollback()
        raise

    return new_attribute


# GET PRODUCT ATTRIBUTES
@router.get("", response_model=list[ProductAttributeResponse])
async def get_product_attribute(product_id: int, db: AsyncSession = Depends(get_db), 
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_attribute = select(ProductAttribute).where(ProductAttribute.product_id == product_id)

    result_attribute = await db.execute(query_attribute)

    attribute = result_attribute.scalars().all()

    if attribute is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Python attribute not found")

    return attribute

# GET PRODUCT ATTRIBUTES ID
@router.get("/{attribute_id}", response_model=ProductAttributeResponse)
async def get_product_attribute_id(product_id: int, attribute_id: int, 
                                   db: AsyncSession = Depends(get_db), 
                                   current_user: User = Depends(require_role("ADMIN"))
                                   ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_attribute = select(ProductAttribute).where(ProductAttribute.product_id == product_id, 
                                                     ProductAttribute.id == attribute_id)

    result_attribute = await db.execute(query_attribute)

    attribute = result_attribute.scalar_one_or_none()

    if attribute is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product attribute not found")

    return attribute

# UPDATE PRODUCT ATTRIBUTE
@router.patch("/{attribute_id}", response_model=ProductAttributeResponse)
async def update_product_attribute(product_id: int, attribute_id: int,  
                                   attribute_data: ProductAttributeUpdate, db: AsyncSession = Depends(get_db), 
                                   current_user: User = Depends(require_role("ADMIN"))
                                   ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_attribute = select(ProductAttribute).where(ProductAttribute.product_id == product_id, 
                                                     ProductAttribute.id == attribute_id)

    result_attribute = await db.execute(query_attribute)

    attribute = result_attribute.scalar_one_or_none()

    if attribute is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product attribute not found")

    update_data = attribute_data.model_dump(exclude_unset=True)

    if "attribute_name" in update_data:
        query_duplicate = select(ProductAttribute).where(ProductAttribute.product_id == product_id, 
                                                         ProductAttribute.attribute_name == update_data["attribute_name"], 
                                                         ProductAttribute.id != attribute_id)

        result_duplicate = await db.execute(query_duplicate)

        duplicate_attribute = result_duplicate.scalar_one_or_none()

        if duplicate_attribute is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Product attribute already exists")


    try:
        for key, value in update_data.items():
            setattr(attribute, key, value)

        await db.commit()
        await db.refresh(attribute)

    except Exception:
        await db.rollback()
        raise

    return attribute


# DELETE PRODUCT ATTRIBUTES
@router.delete("/{attribute_id}")
async def delete_product_attribute(product_id: int, attribute_id: int, 
                                   db: AsyncSession = Depends(get_db), 
                                   current_user: User = Depends(require_role("ADMIN"))
                                   ):

    query_product = select(Product).where(Product.id == product_id)

    result_product = await db.execute(query_product)

    product = result_product.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    query_attribute = select(ProductAttribute).where(ProductAttribute.product_id == product_id, 
                                                     ProductAttribute.id == attribute_id)

    result_attribute = await db.execute(query_attribute)

    attribute = result_attribute.scalar_one_or_none()

    if attribute is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product attribute not found")

    try:
        await db.delete(attribute)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {"message" : "Product attribute deleted successfully"}