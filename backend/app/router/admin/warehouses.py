from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.model_database.inventory.warehouse import Warehouse
from app.schemas.warehouse import (
    WarehouseCreate, 
    WarehouseResponse, 
    WarehouseStatusUpdate,
    WarehouseUpdate
)
from app.core.security import require_role
from app.model_database.users.user import User
from app.model_database.inventory.inventory import Inventory



admin = APIRouter(prefix="/admin/warehouses", tags=["Warehouses Management"])


# CREATE WAREHOUSE
@admin.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(warehouse_data: WarehouseCreate,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    query = select(Warehouse).where(Warehouse.name == warehouse_data.name)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Warehouse name already exists")

    new_warehouse = Warehouse(**warehouse_data.model_dump())

    try:
        db.add(new_warehouse)
        await db.commit()
        await db.refresh(new_warehouse)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to create warhouse")
        

    return new_warehouse


# GET WAREHOUSE
@admin.get("", response_model=list[WarehouseResponse])
async def get_warehouse(db: AsyncSession = Depends(get_db), 
                        current_user: User = Depends(require_role("ADMIN"))
                        ):

    query = select(Warehouse)

    result = await db.execute(query)

    warehouse = result.scalars().all()

    return warehouse


# GET WAREHOUSE ID
@admin.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse_id(warehouse_id: int, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    query = select(Warehouse).where(Warehouse.id == warehouse_id)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Warehouse not found")

    return warehouse


# UPDATE WAREHOUSE 
@admin.patch("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(warehouse_id: int, warehouse_data: WarehouseUpdate,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    query = select(Warehouse).where(Warehouse.id == warehouse_id)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Warehouse not found")

    update_data = warehouse_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        query = select(Warehouse).where(Warehouse.name == update_data["name"],
                                        Warehouse.id != warehouse_id)

        result = await db.execute(query)

        warehouse_name = result.scalar_one_or_none()

        if warehouse_name is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Warehouse name already exists")

    for key, value in update_data.items():
        setattr(warehouse, key, value)

    try:
        await db.commit()
        await db.refresh(warehouse)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to update warhouse")
        

    return warehouse


# UPDATE WAREHOUSE STATUS
@admin.patch("/{warehouse_id}/status", response_model=WarehouseResponse)
async def update_warehouse_status(warehouse_id: int, warehouse_data: WarehouseStatusUpdate,
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    query = select(Warehouse).where(Warehouse.id == warehouse_id)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Warehouse not found")

    warehouse.is_active = warehouse_data.is_active

    try:
        await db.commit()
        await db.refresh(warehouse)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to update warhouse status")
        

    return warehouse


# DELETE WAREHOUSE
@admin.delete("/{warehouse_id}", status_code=status.HTTP_200_OK)
async def delete_warehouse(warehouse_id: int, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    query = select(Warehouse).where(Warehouse.id == warehouse_id)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Warehouse not found")


    query = select(Inventory).where(Inventory.warehouse_id == warehouse_id)

    result = await db.execute(query)

    inventory = result.scalar_one_or_none()

    if inventory is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Inventory already exists")

    try:
        await db.delete(warehouse)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to delete warhouse")
        

    return {"message" : "Warehouse deleted successfully"}