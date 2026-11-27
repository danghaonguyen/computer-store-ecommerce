from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


from app.model_database.orders.order import Order
from app.model_database.shipments.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate

# REQUIRED ROLE - ADMIN
# CREATE SHIPMENT
async def create_shipment(db: AsyncSession, shipment_data: ShipmentCreate):

    # Check order
    query = select(Order).where(Order.id == shipment_data.order_id)

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    # Check shipment
    query = select(Shipment).where(Shipment.order_id == order.id)

    result = await db.execute(query)

    existing_shipment = result.scalar_one_or_none()

    if existing_shipment is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Shipment already exists for this order")


    if order.status != "PROCESSING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Order must be in PROCESSING status to create shipment")


    new_shipment = Shipment(**shipment_data.model_dump())

    try:
        db.add(new_shipment)
        await db.commit()
        await db.refresh(new_shipment)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to create shipment")

    return new_shipment


# VIEW ALL SHIPMENT
async def get_shipments(db: AsyncSession):
    query = select(Shipment)

    result = await db.execute(query)

    shipments = result.scalars().all()

    return shipments


# VIEW SHIPMENT BY ID
async def get_shipment_id(db: AsyncSession, shipmemt_id: int):

    query = select(Shipment).where(Shipment.id == shipmemt_id)

    result = await db.execute(query)

    shipment = result.scalar_one_or_none()

    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Shipment not found")

    return shipment

# UPDATE SHIPMENT BY ID
async def update_shipment_id(db: AsyncSession, shipment_id: int, 
                             shipment_data: ShipmentUpdate):

    query = select(Shipment).where(Shipment.id == shipment_id)

    result = await db.execute(query)

    shipment = result.scalar_one_or_none()

    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Shipment not found")

    update_data = shipment_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(shipment, key, value)

    try:
        await db.commit()
        await db.refresh(shipment)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to update info shipment") 

    return shipment

# ===========================================================

# REQUIRED ROLE - CUSTOMER
# VIEW ORDER SHIPMENT
async def view_order_shipment(db: AsyncSession, order_id: int, 
                             user_id: int):

    # Check order
    query = select(Order).where(Order.id == order_id,
                                Order.user_id == user_id)

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    # Check shipment
    query = select(Shipment).where(Shipment.order_id == order.id)

    result = await db.execute(query)

    shipment = result.scalar_one_or_none()

    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Shipment not found")

    return shipment


# VIEW SHIPMENT BY ID
async def view_shipment_id(db: AsyncSession, shipment_id: int, 
                          user_id: int):


    query = select(Shipment).join(Order, Shipment.order_id == Order.id).where(
        Shipment.id == shipment_id, Order.user_id == user_id)

    result = await db.execute(query)

    shipment = result.scalar_one_or_none()

    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Shipment not found")

    return shipment