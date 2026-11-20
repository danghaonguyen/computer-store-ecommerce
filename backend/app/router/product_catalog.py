from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.model_database.products.product import Product
from app.model_database.products.product_variant import ProductVariant
from app.schemas.product_catalog import ProductCatalogDetailResponse
from app.schemas.product import ProductResponse


router = APIRouter(prefix="/catalog/products", tags=["Product Catalog"])


# GET ACTIVE PRODUCT
@router.get("", response_model=list[ProductResponse])
async def get_catalog_products(db: AsyncSession = Depends(get_db)):

    query = select(Product).where(Product.is_active == True)

    result = await db.execute(query)

    products = result.scalars().all()

    return products


# GET PRODUCT
@router.get("/{product_id}", response_model=ProductCatalogDetailResponse)
async def get_catalog_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):


    query = select(Product).options(

        selectinload(Product.category), 
        selectinload(Product.brand),
        selectinload(Product.variants.and_(
            ProductVariant.is_active == True
        )),

        selectinload(Product.images),
        selectinload(Product.attributes)

    ).where(

        Product.id == product_id, 
        Product.is_active == True
    )

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Product not found")

    return product