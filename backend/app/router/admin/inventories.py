from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.inventory.inventory import Inventory
from app.model_database.inventory.warehouse import Warehouse
from app.model_database.products.product_variant import ProductVariant
from app.model_database.users.user import User
from app.schemas.inventory import InventoryCreate, InventoryResponse


admin = APIRouter(prefix="/admin/inventories", tags=["Inventories Management"])


# CREATE INVENTORY
@admin.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(inventory_data: InventoryCreate,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    # Check Warehouse
    query = select(Warehouse).where(Warehouse.id == inventory_data.warehouse_id)

    result = await db.execute(query)

    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Warehouse not found")

    # Check Product Variant
    query = select(ProductVariant).where(ProductVariant.id == inventory_data.product_variant_id)

    result = await db.execute(query)

    product_variant = result.scalar_one_or_none()

    if product_variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product variant not found")

    # Check Inventory
    query = select(Inventory).where(Inventory.warehouse_id == inventory_data.warehouse_id,
                                    Inventory.product_variant_id == inventory_data.product_variant_id)

    result = await db.execute(query)

    existing_inventory = result.scalar_one_or_none()

    if existing_inventory is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Inventory already exists")

    # Create new inventory
    new_inventory = Inventory(quantity=0, reserved_quantity=0, **inventory_data.model_dump())

    try:
        db.add(new_inventory)
        await db.commit()
        await db.refresh(new_inventory)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to create inventory")

    return new_inventory


# GET INVENTORY
@admin.get("", response_model=list[InventoryResponse])
async def get_inventory(db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Inventory)

    result = await db.execute(query)

    inventories = result.scalars().all()

    return inventories


# GET INVENTORY ID
@admin.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_id(inventory_id: int, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    query = select(Inventory).where(Inventory.id == inventory_id)

    result = await db.execute(query)

    inventory = result.scalar_one_or_none()

    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inventory not found")

    return inventory