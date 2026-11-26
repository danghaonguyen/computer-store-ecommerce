from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import require_role
from app.services.shipment_service import view_order_shipment
from app.schemas.shipment import ShipmentResponse
from app.database.database import get_db
from app.model_database.users.user import User


customer = APIRouter(prefix="/orders-shipment", tags=["Orders Shipment - Customer"])


# VIEW ALL ORDER SHIPMENT
@customer.get("/{order_id}/shipment", response_model=ShipmentResponse)
async def get_order_shipment_api(order_id: int, db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(require_role("CUSTOMER"))
                                 ):

    return await view_order_shipment(db, order_id, current_user.id)
