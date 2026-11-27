from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.model_database.inventory.supplier import Supplier
from app.model_database.inventory.stock_movement import StockMovement
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.core.security import require_role
from app.model_database.users.user import User


admin = APIRouter(prefix="/admin/suppliers", tags=["Suppliers Management"])


# CREATE SUPPLIER
@admin.post("", response_model=SupplierResponse)
async def create_supplier(supplier_data: SupplierCreate,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Supplier).where(Supplier.name == supplier_data.name)

    result = await db.execute(query)

    supplier = result.scalar_one_or_none()

    if supplier is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Supplier already exists")

    new_supplier = Supplier(**supplier_data.model_dump())

    try:
        db.add(new_supplier)
        await db.commit()
        await db.refresh(new_supplier)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to create supplier")
        

    return new_supplier

# GET SUPPLIER
@admin.get("", response_model=list[SupplierResponse])
async def get_supplier(db: AsyncSession = Depends(get_db), 
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = select(Supplier).order_by(Supplier.created_at.desc())

    result = await db.execute(query)

    suppliers = result.scalars().all()

    return suppliers


# GET SUPPLIER ID
@admin.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier_id(supplier_id: int, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Supplier).where(Supplier.id == supplier_id)

    result = await db.execute(query)

    supplier = result.scalar_one_or_none()

    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Supplier not found")

    return supplier

# UPDATE SUPPLIER ID
@admin.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: int, supplier_data: SupplierUpdate,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Supplier).where(Supplier.id == supplier_id)

    result = await db.execute(query)

    supplier = result.scalar_one_or_none()

    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Supplier not found")


    update_data = supplier_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        query = select(Supplier).where(Supplier.name == update_data["name"],
                                       Supplier.id != supplier_id)

        result = await db.execute(query)

        supplier_name = result.scalar_one_or_none()

        if supplier_name is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Supplier name already exists")

    if update_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No fields provided for update")
    

    for key, value in update_data.items():
        setattr(supplier, key, value)

    try:
        await db.commit()
        await db.refresh(supplier)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update info supplier")

    return supplier


# DELETE SUPPLIER 
@admin.delete("/{supplier_id}", status_code=status.HTTP_200_OK)
async def delete_supplier(supplier_id: int, 
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Supplier).where(Supplier.id == supplier_id)

    result = await db.execute(query)

    supplier = result.scalar_one_or_none()

    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Supplier not found")

    # Check stock movement history
    query = select(StockMovement.id).where(StockMovement.supplier_id == supplier_id)

    result = await db.execute(query)

    stock_movement = result.scalar_one_or_none()

    if stock_movement is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot delete supplier because stock movement history exists")

    try:
        await db.delete(supplier)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to delete supplier")

    return {"message" : "Supplier deleted successfully"}
    