from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.model_database.products.brand import Brand
from app.schemas.brand import (
    BrandCreate, 
    BrandResponse, 
    BrandUpdate, 
    BrandStatusUpdate
    )
from app.core.security import require_role
from app.model_database.users.user import User


router = APIRouter(prefix="/brands", tags=["Brands"])

# CREATED BRAND
@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand_data: BrandCreate, 
                       db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Brand).where(Brand.name == brand_data.name)

    result = await db.execute(query)

    brand_name = result.scalar_one_or_none()

    if brand_name:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Brand name already exists")

    query = select(Brand).where(Brand.slug == brand_data.slug)

    result = await db.execute(query)
    brand_slug = result.scalar_one_or_none()

    if brand_slug:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Brand slug already exists")

    new_brand = Brand(**brand_data.model_dump())

    db.add(new_brand)
    await db.commit()
    await db.refresh(new_brand)

    return new_brand



# GET BRAND
@router.get("", response_model=list[BrandResponse])
async def get_brand(db: AsyncSession = Depends(get_db), 
                    current_user: User = Depends(require_role("ADMIN"))
                    ):

    query = select(Brand)

    result = await db.execute(query)

    brands = result.scalars().all()

    return brands


# GET BRAND ID
@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand_id(brand_id: int, 
                       db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Brand).where(Brand.id == brand_id)

    result = await db.execute(query)

    brands = result.scalar_one_or_none()

    if brands is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Brand not found")

    return brands

# UPDATE BRAND 
@router.patch("/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: int, brand_data: BrandUpdate, 
                       db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Brand).where(Brand.id == brand_id)

    result = await db.execute(query)

    brand = result.scalar_one_or_none()

    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Brand not found")

    update_data= brand_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        query = select(Brand).where(Brand.name == update_data["name"],
                                    Brand.id != brand_id)

        result = await db.execute(query)

        existing_brand = result.scalar_one_or_none()

        if existing_brand:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Brand name already exists")

    if "slug" in update_data:
        query = select(Brand).where(Brand.slug == update_data["slug"], 
                                    Brand.id != brand_id)

        result = await db.execute(query)

        existing_brand = result.scalar_one_or_none()

        if existing_brand:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Brand slug already exists")


    for key, value in update_data.items():
        setattr(brand, key, value)

    await db.commit()
    await db.refresh(brand)

    return brand


# UPDATE BRAND STATUS
@router.patch("/{brand_id}/status", response_model=BrandResponse)
async def update_brand_status(brand_id: int, brand_data: BrandStatusUpdate, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    query = select(Brand).where(Brand.id == brand_id)

    result = await db.execute(query)

    brand = result.scalar_one_or_none()

    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Brand not found")

    brand.is_active = brand_data.is_active

    await db.commit()
    await db.refresh(brand)

    return brand

# DELETE BRAND
@router.delete("/{brand_id}")
async def delete_brand(brand_id: int, 
                       db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Brand).where(Brand.id == brand_id)

    result = await db.execute(query)

    brand = result.scalar_one_or_none()

    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Brand not found")

    await db.delete(brand)
    await db.commit()

    return {"message" : "Brand deleted successfully"}
