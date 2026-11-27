from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.model_database.users.user import User
from app.schemas.shipment import (
    ShipmentCreate, 
    ShipmentResponse,
    ShipmentUpdate
)
from app.services.shipment_service import (
    create_shipment, 
    get_shipments,
    get_shipment_id,
    update_shipment_id
)
from app.core.security import require_role


admin = APIRouter(prefix="/admin/shipments", tags=["Shipments Management"])

# CREATE SHIPMENT
@admin.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment_api(shipment_data: ShipmentCreate,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    return await create_shipment(db, shipment_data)


# VIEW ALL SHIPMENT
@admin.get("", response_model=list[ShipmentResponse])
async def get_shipment_api(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("ADMIN"))
                           ):

    return await get_shipments(db)


# VIEW SHIPMENT BY ID
@admin.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment_id_api(shipment_id: int, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    return await get_shipment_id(db, shipment_id)

# UPDATE SHIPMENT BY ID
@admin.patch("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment_id_api(shipment_id: int, shipment_data: ShipmentUpdate,
                                 db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(require_role("ADMIN"))
                                 ):

    return await update_shipment_id(db, shipment_id, shipment_data)