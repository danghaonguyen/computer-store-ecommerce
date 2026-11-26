from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.model_database.inventory.stock_movement import StockMovement
from app.model_database.inventory.inventory import Inventory
from app.model_database.inventory.supplier import Supplier

from app.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementResponse
)

from app.core.security import require_role
from app.model_database.users.user import User



admin = APIRouter(prefix="/admin/stock-movements", tags=["Stock Movements - Admin"])


# CREATE STOCK MOVEMENT
@admin.post("", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_movement(payload: StockMovementCreate,
                                db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query = (select(Inventory).where(Inventory.id == payload.inventory_id).with_for_update())

    result = await db.execute(query)

    inventory = result.scalar_one_or_none()

    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inventory not found")

    # Check supplier
    if payload.movement_type == "IN" and payload.supplier_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier is required for stock IN"
        )

    if payload.supplier_id is not None:
        query = select(Supplier.id).where(Supplier.id == payload.supplier_id)

        result = await db.execute(query)

        supplier = result.scalar_one_or_none()

        if supplier is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Supplier not found")


    # Update inventory quantity
    if payload.movement_type in ["IN", "ADJUSTMENT_IN"]:
        inventory.quantity += payload.quantity

    elif payload.movement_type in ["OUT", "ADJUSTMENT_OUT"]:

        available_quantity = (inventory.quantity - inventory.reserved_quantity)

        if payload.quantity > available_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Insufficient available inventory")

        inventory.quantity -= payload.quantity

    # Create new stock movement
    stock_movement = StockMovement(**payload.model_dump())

    try:
        db.add(stock_movement)
        await db.commit()
        await db.refresh(stock_movement)

    except Exception:
        await db.rollback()
        raise

    return stock_movement


# GET STOCK MOVEMENT
@admin.get("", response_model=list[StockMovementResponse])
async def get_stock_movement(db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(require_role("ADMIN"))
                             ):

    query = select(StockMovement).order_by(StockMovement.created_at.desc())

    result = await db.execute(query)

    stock_movement = result.scalars().all()

    return stock_movement


# GET STOCK MOVEMENT ID
@admin.get("/{stock_movement_id}", response_model=StockMovementResponse)
async def get_stock_movement_id(stock_movement_id: int, 
                                db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(require_role("ADMIN"))
                                ):

    query = select(StockMovement).where(StockMovement.id == stock_movement_id)

    result = await db.execute(query)

    stock_movement = result.scalar_one_or_none()

    if stock_movement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stock movement not found")

    return stock_movement