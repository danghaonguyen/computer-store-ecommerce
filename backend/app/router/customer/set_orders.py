from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import require_role
from app.database.database import get_db
from app.model_database.products.product_variant import ProductVariant
from app.model_database.carts.cart import Cart
from app.model_database.carts.cart_item import CartItem
from app.model_database.orders.order import Order
from app.model_database.orders.order_item import OrderItem
from app.model_database.orders.order_status_history import OrderStatusHistory
from app.model_database.users.user import User
from app.model_database.inventory.inventory import Inventory
from app.model_database.orders.order_item_inventory import OrderItemInventory
from app.schemas.order import (
    OrderCreate, 
    OrderDetailResponse, 
    OrderStatusHistoryResponse
)
from datetime import datetime, timezone
from sqlalchemy import func
from app.model_database.promotions.coupon import Coupon
from app.model_database.promotions.coupon_usage import CouponUsage
from decimal import Decimal
from uuid import uuid4


customer = APIRouter(prefix="/orders", tags=["Orders - Customer"])

# CUSTOMER =============================
# CREATE ORDER
@customer.post("", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
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

        # Check coupon
        coupon = None
        discount_amount = Decimal("0.00")

        if order_data.coupon_code is not None:

            query = select(Coupon).where(

                Coupon.code == order_data.coupon_code

            ).with_for_update()

            result = await db.execute(query)

            coupon = result.scalar_one_or_none()

            if coupon is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail="Coupon not found")

            if not coupon.is_active:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Coupon is inactive")

            now = datetime.now(timezone.utc)

            if now < coupon.start_at or now > coupon.end_at:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Coupon is  not available at this time")

            if subtotal < coupon.minimum_order_amount:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Order amount does not meet coupon minium")

            if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Coupon usage limit exceeded")

            query = select(func.count(CouponUsage.id)).where(

                CouponUsage.coupon_id == coupon.id,
                CouponUsage.user_id == current_user.id

            )

            result = await db.execute(query)

            user_used_count = result.scalar_one()

            if user_used_count >= coupon.usage_limit_per_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You have exceeded the coupon usage limit")

            # Calculate discount
            if coupon.discount_type == "PERCENTAGE":

                discount_amount = subtotal * coupon.discount_value / Decimal("100")

                if coupon.maximum_discount_amount is not None:

                    discount_amount = min(discount_amount, coupon.maximum_discount_amount)

            else:
                discount_amount = coupon.discount_value

            # Discount cannot exceed subtotal
            discount_amount = min(discount_amount, subtotal)

        # Create shipping fee and discount amount
        shipping_fee = Decimal("0.00")

        total_amount = subtotal - discount_amount + shipping_fee

        order_number = f"ORD-{uuid4().hex[:12].upper()}"

        new_order = Order(

            **order_data.model_dump(exclude={"coupon_code"}),
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

        # Create coupon usage
        if coupon is not None:

            coupon_usage = CouponUsage(
                coupon_id=coupon.id,
                user_id=current_user.id,
                order_id=new_order.id,
                discount_amount=discount_amount
            )

            db.add(coupon_usage)

            coupon.used_count += 1


        await db.commit()
        await db.refresh(new_order)

        order_query = select(Order).options(

            selectinload(Order.items)

        ).where(Order.id == new_order.id)

        result = await db.execute(order_query)
        order_result = result.scalar_one()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to create order")

    return order_result


# GET ORDER
@customer.get("", response_model=list[OrderDetailResponse])
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
@customer.get("/{order_id}", response_model=OrderDetailResponse)
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
@customer.get("/{order_id}/history", response_model=list[OrderStatusHistoryResponse])
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
@customer.patch("/{order_id}/cancel")
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to update order")

    return order


