from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.orders.order import Order
from app.model_database.orders.order_item import OrderItem
from app.model_database.orders.order_status_history import OrderStatusHistory
from app.model_database.users.user import User
from app.model_database.inventory.inventory import Inventory
from app.model_database.orders.order_item_inventory import OrderItemInventory
from app.model_database.inventory.stock_movement import StockMovement
from app.schemas.order import ( 
    OrderStatusUpdate,
    OrderStatusHistoryResponse,
    OrderResponse,
    OrderDetailResponse
)

admin = APIRouter(prefix="/admin/orders", tags=["Orders - Admin"])


# ADMIN =================================

# UPDATE ORDERS STATUS
@admin.patch("/{order_id}/status")
async def update_order_status(order_id: int, order_data: OrderStatusUpdate,
                              db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(require_role("ADMIN"))
                              ):

    try:
        query = select(Order).where(Order.id == order_id).with_for_update()

        result = await db.execute(query)

        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order not found")


        allowed_transitions = {

            "PENDING" : ["CONFIRMED"],
            "CONFIRMED" : ["PROCESSING"],
            "PROCESSING" : ["SHIPPED"],
            "SHIPPED" : ["DELIVERED"]
        }

        if order_data.status not in allowed_transitions.get(order.status, []):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Cannot change order status from {order.status} to {order_data.status}")


        if order_data.status == "DELIVERED":

            query = select(OrderItemInventory).join(OrderItem).where(OrderItem.order_id == order_id)

            result = await db.execute(query)

            allocations = result.scalars().all()

            for allocation in allocations:

                query = select(Inventory).where(Inventory.id == allocation.inventory_id).with_for_update()

                result = await db.execute(query)

                inventory = result.scalar_one()

                inventory.quantity -= allocation.quantity
                inventory.reserved_quantity -= allocation.quantity

                stock_movement = StockMovement(

                    inventory_id=inventory.id,
                    supplier_id=None,
                    movement_type="OUT",
                    quantity=allocation.quantity,
                    note=f"Order delivered: {order.order_number}"
                )

                db.add(stock_movement)   

        order.status = order_data.status

        order_history = OrderStatusHistory(

            order_id=order.id,
            changed_by=current_user.id,
            status=order_data.status,
            note=order_data.note

        )

        db.add(order_history)

        await db.commit()
        await db.refresh(order)

    except Exception:
        await db.rollback()
        raise

    return order

# GET ORDER STATUS HISTORY
@admin.get("/{order_id}/history", response_model=list[OrderStatusHistoryResponse])
async def get_order_status_history_admin(order_id: int, db: AsyncSession = Depends(get_db),
                                         current_user: User = Depends(require_role("ADMIN"))
                                         ):


    query = select(Order).where(Order.id == order_id)

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    query = select(OrderStatusHistory).where(
        OrderStatusHistory.order_id == order_id).order_by(OrderStatusHistory.created_at.desc())

    result = await db.execute(query)

    order_history = result.scalars().all()

    return order_history

# GET ORDER
@admin.get("", response_model=list[OrderResponse])
async def get_order(db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(require_role("ADMIN"))
                    ):

    query = select(Order).order_by(Order.created_at.desc())

    result = await db.execute(query)

    order = result.scalars().all()

    return order


# GET ORDER ID
@admin.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order_id(order_id: int, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(require_role("ADMIN"))
                       ):

    query = (select(Order).options(selectinload(Order.items)).where(Order.id == order_id))

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    return order