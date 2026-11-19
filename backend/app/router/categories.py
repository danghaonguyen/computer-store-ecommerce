from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.model_database.products.category import Category
from app.model_database.users.user import User
from app.schemas.category import (
     CategoryCreate, 
     CategoryResponse, 
     CategoryUpdate, 
     CategoryStatusUpdate
     )
from app.core.security import require_role

router = APIRouter(prefix="/categories", tags=["Categories"])

# CREATE CATEGORY
@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, 
                          db: AsyncSession = Depends(get_db), 
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Category).where(Category.slug == category_data.slug)

    result = await db.execute(query)

    category = result.scalar_one_or_none()

    if category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Category slug already exists")


    if category_data.parent_id is not None:
        query = select(Category).where(Category.id == category_data.parent_id)

        result = await db.execute(query)

        parent_category = result.scalar_one_or_none()

        if parent_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Parent category not found")

        
    new_category = Category(**category_data.model_dump())

    try:
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

    except Exception:
        await db.rollback()
        raise

    return new_category


# GET CATEGORIES
@router.get("", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(require_role("ADMIN"))
                         ):

    query = select(Category)

    result = await db.execute(query)

    categories = result.scalars().all()

    return categories


# GET CATEGORY ID
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Category).where(Category.id == category_id)

    result = await db.execute(query)

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Category not found")

    return category


# UPDATE CATEGORY ID
@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_data: CategoryUpdate, 
                          db: AsyncSession = Depends(get_db), 
                          current_user: User = Depends(require_role("ADMIN"))):

    query = select(Category).where(Category.id == category_id)

    result = await db.execute(query)

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Category not found")

    update_data = category_data.model_dump(exclude_unset=True)

    if "slug" in update_data:
            query = select(Category).where(Category.slug == update_data["slug"], 
                                           Category.id != category_id)
    
            result = await db.execute(query)
    
            existing_category = result.scalar_one_or_none()
    
            if existing_category:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                    detail="Category slug already exists")

    if "parent_id" in update_data and update_data["parent_id"] is not None:

        if update_data["parent_id"] == category_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                    detail="Category cannot be its own parent")
        
        query = select(Category).where(Category.id == update_data["parent_id"])

        result = await db.execute(query)

        parent_category = result.scalar_one_or_none()

        if parent_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Parent category not found") 

    for key, value in update_data.items():
        setattr(category, key, value)

    try:
        await db.commit()
        await db.refresh(category)

    except Exception:
        await db.rollback()
        raise

    return category


# UPDATE CATEGORY STATUS
@router.patch("/{category_id}/status")
async def update_category_status(category_id: int, category_data: CategoryStatusUpdate, 
                                 db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(require_role("ADMIN"))
                                 ):

    query = select(Category).where(Category.id == category_id)

    result = await db.execute(query)
     
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="ID Category not found")

    category.is_active = category_data.is_active

    try:
        await db.commit()
        await db.refresh(category)

    except Exception:
        await db.rollback()
        raise

    return category


# DELETE CATEGORY
@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), 
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Category).where(Category.id == category_id)

    result = await db.execute(query)

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                              detail="ID Category not found")

    try:
        await db.delete(category)
        await db.commit()

    except Exception:
        await db.rollback()
        raise
    
    return {"message" : "Category deleted successfully"}

