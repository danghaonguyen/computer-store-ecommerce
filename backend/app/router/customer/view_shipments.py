from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import require_role
from app.services.shipment_service import view_shipment_id
from app.schemas.shipment import ShipmentResponse
from app.database.database import get_db
from app.model_database.users.user import User


customer = APIRouter(prefix="/shipment", tags=["Shipments - Customer"])


# VIEW SHIPMENT BY ID
@customer.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment_api(shipment_id: int, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role("CUSTOMER"))
                           ):

    return await view_shipment_id(db, shipment_id, current_user.id)

