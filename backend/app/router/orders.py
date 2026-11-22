from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.products.product import Product
from app.model_database.products.product_variant import ProductVariant
from app.model_database.carts.cart import Cart
from app.model_database.carts.cart_item import CartItem
from app.model_database.orders.order import Order
from app.model_database.orders.order_item import OrderItem
from app.model_database.orders.order_status_history import OrderStatusHistory
from app.model_database.users.user import User
from app.model_database.inventory.inventory import Inventory
from app.model_database.orders.order_item_inventory import OrderItemInventory
from app.model_database.inventory.stock_movement import StockMovement
from app.schemas.order import (
    OrderCreate, 
    OrderDetailResponse, 
    OrderStatusUpdate,
    OrderStatusHistoryResponse
)
from decimal import Decimal
from uuid import uuid4


router = APIRouter(prefix="/orders", tags=["Orders"])

# CUSTOMER =============================
# CREATE ORDER
@router.post("", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(require_role("CUSTOMER"))
                       ):
    
    # Check cart 
    query = select(Cart).options(

        selectinload(Cart.items)
        .selectinload(CartItem.product_variant)
        .selectinload(ProductVariant.product)

    ).where(Cart.user_id == current_user.id)

    result = await db.execute(query)

    carts = result.scalar_one_or_none()

    if carts is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cart is empty")

    if not carts.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cart is empty")

    try:
        # Check cart items
        for item in carts.items:
            variant = item.product_variant
            product = variant.product
        
            if not variant.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Product variant is inactive")
        
            if not product.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Product is inactive")


        # Total all product for order
        subtotal = Decimal("0.00")

        for item in carts.items:
            price_variant = item.product_variant.price

            subtotal += price_variant * item.quantity

        
        # Create shipping fee and discount amount
        shipping_fee = Decimal("0.00")

        discount_amount = Decimal("0.00")

        total_amount = subtotal + shipping_fee - discount_amount

        order_number = f"ORD-{uuid4().hex[:12].upper()}"

        new_order = Order(

            **order_data.model_dump(),
            user_id=current_user.id,
            order_number=order_number,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            discount_amount=discount_amount,
            total_amount=total_amount,
            items=[]

        )

        db.add(new_order)
        await db.flush()


        for item in carts.items:
            variant = item.product_variant
            product = variant.product

            order_item = OrderItem(

                order_id=new_order.id,
                product_variant_id=variant.id,
                product_name=product.name,
                variant_name=variant.variant_name,
                sku=variant.sku,
                unit_price=variant.price,
                quantity=item.quantity,
                subtotal=variant.price * item.quantity

            )

            new_order.items.append(order_item)


        await db.flush()

        # Allocate inventory for order items
        for order_item in new_order.items:

            query = select(Inventory).where(
                Inventory.product_variant_id == order_item.product_variant_id
            ).order_by(Inventory.id).with_for_update()

            result = await db.execute(query)
            inventories = result.scalars().all()

            remaining_quantity = order_item.quantity

            for inventory in inventories:

                available_quantity = inventory.quantity - inventory.reserved_quantity

                if available_quantity <= 0:
                    continue

                reserve_quantity = min(available_quantity, remaining_quantity)

                inventory.reserved_quantity += reserve_quantity

                remaining_quantity -= reserve_quantity

                allocation = OrderItemInventory(
                    order_item_id=order_item.id,
                    inventory_id=inventory.id,
                    quantity=reserve_quantity
                )

                db.add(allocation)

                if remaining_quantity == 0:
                    break

            # Check insufficient stock for this order item
            if remaining_quantity > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product variant {order_item.product_variant_id}")

        for item in carts.items:
            await db.delete(item)


        await db.commit()
        await db.refresh(new_order)

        order_query = select(Order).options(

            selectinload(Order.items)

        ).where(Order.id == new_order.id)

        result = await db.execute(order_query)
        order_result = result.scalar_one()

    except Exception:
        await db.rollback()
        raise

    return order_result


# GET ORDER
@router.get("", response_model=list[OrderDetailResponse])
async def get_order(db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(require_role("CUSTOMER"))
                    ):

    query = select(Order).options(

        selectinload(Order.items)

    ).where(Order.user_id == current_user.id)

    result = await db.execute(query)

    order = result.scalars().all()

    return order


# GET ORDER ID
@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order_id(order_id: int, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(require_role("CUSTOMER"))
                       ):

    query = select(Order).options(

        selectinload(Order.items)

    ).where(Order.id == order_id, Order.user_id == current_user.id)

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    return order


# GET ORDER STATUS HISTORY
@router.get("/{order_id}/history", response_model=list[OrderStatusHistoryResponse])
async def get_order_status_history(order_id: int, db: AsyncSession = Depends(get_db),
                                   current_user: User = Depends(require_role("CUSTOMER"))
                                   ):

    query = select(Order).where(Order.id == order_id, Order.user_id == current_user.id)

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


# UPDATE ORDER
@router.patch("/{order_id}/cancel")
async def update_order(order_id: int, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(require_role("CUSTOMER"))
                   ):
    try:
        # Check order
        query = select(Order).where(Order.id == order_id, 
                                    Order.user_id == current_user.id).with_for_update()

        result = await db.execute(query)

        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order not found")

        if order.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Only pending orders can be cancelled")


        # Check order item & inventory
        query = select(OrderItemInventory).join(OrderItem).where(OrderItem.order_id == order.id)

        result = await db.execute(query)

        allocations = result.scalars().all()

        for allocation in allocations:

            query = select(Inventory).where(

                Inventory.id == allocation.inventory_id

            ).with_for_update()

            result = await db.execute(query)

            inventory = result.scalar_one()

            inventory.reserved_quantity -= allocation.quantity


        order.status = "CANCELLED"

        order_history = OrderStatusHistory(

            order_id=order.id,
            changed_by=current_user.id,
            status="CANCELLED",
            note="Order cancelled by customer"
        )

        db.add(order_history)

        await db.commit()
        await db.refresh(order)

    except Exception:
        await db.rollback()
        raise

    return order

# ADMIN =================================

# UPDATE ORDERS STATUS
@router.patch("/{order_id}/status")
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
@router.get("/admin/{order_id}/history", response_model=list[OrderStatusHistoryResponse])
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
