import json
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.core.security import require_role

from app.model_database.users.user import User
from app.model_database.orders.order import Order
from app.model_database.payments.payment import Payment
from app.model_database.payments.payment_transaction import PaymentTransaction

from app.schemas.payment import (
    PaymentCheckoutResponse, 
    PaymentDetailResponse,
)

from app.services.zalopay_service import ZaloPayService


customer = APIRouter(prefix="/payments", tags=["Payments - Customer"])


# CUSTOMER =====================================
# CREATE PAYMENT
@customer.post("/orders/{order_id}", response_model=PaymentCheckoutResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(order_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(require_role("CUSTOMER"))
                         ):

    # Check order
    query = select(Order).options(

        selectinload(Order.items)

    ).where(Order.id == order_id, Order.user_id == current_user.id).with_for_update()

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    if order.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Only pending orders can be paid")


    # Get payment
    query = select(Payment).where(Payment.order_id == order_id).with_for_update()

    result = await db.execute(query)

    payment = result.scalar_one_or_none()

    if payment is not None:

        if payment.payment_status != "FAILED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Payment already exists or is being processed")


        payment.payment_status = "PENDING"

    else:

        payment = Payment(

            order_id=order.id,
            payment_method="ZALOPAY",
            payment_status="PENDING",
            amount=order.total_amount

        )

        db.add(payment)
        await db.flush()


    amount = int(order.total_amount)

    if Decimal(amount) != order.total_amount or amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid order amount")


    # Generate transaction code
    app_trans_id = (

        f"{datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')):%y%m%d}"
        f"_{order.id}_{uuid4().hex[:8]}"
    )

    # Create payment transaction
    transaction = PaymentTransaction(

        payment_id=payment.id,
        transaction_code=app_trans_id,
        transaction_type="PAYMENT",
        amount=order.total_amount

    )

    db.add(transaction)
    await db.flush()

    payment_id = payment.id
    transaction_id = transaction.id

    # Save payment before calling Zalopay
    await db.commit()

    # Prepare Zalopay items
    items = [
        {
            "itemid": str(item.product_variant_id),
            "itename": f"{item.product_name} - {item.variant_name}",
            "itemprice": int(item.unit_price),
            "itemquantity": item.quantity
        }
        for item in order.items
    ]

    # Create Zalopay order
    zalopay = ZaloPayService()

    try:

        response = await zalopay.create_order(
            amount=amount,
            app_user=str(current_user.id),
            app_trans_id=app_trans_id,
            description=f"Payment for {order.order_number}",
            items=items

        )

    except Exception:

        # Keep PENDING because the payment result is unkown
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot connect to ZaloPay, Payment status is pending"
        )

    # Check Zalopay response
    if response.get("returncode") != 1:

        transaction.transaction_status = "FAILED"
        transaction.gateway_response = json.dumps(response, ensure_ascii=False)

        payment.payment_status = "FAILED"

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.get(

                "returnmessage",
                "Zalopay order creation failed"
            )
        )

    if not response.get("orderurl"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ZaloPay did not return payment URL")

    # Save gateway response
    transaction.gateway_response = json.dumps(response, ensure_ascii=False)
    print("Zalopay response:", response)

    await db.commit()

    return PaymentCheckoutResponse(
        payment_id=payment_id,
        transaction_id=transaction_id,
        transaction_code=app_trans_id,
        payment_status="PENDING",
        amount=order.total_amount,
        qr_code=response["qrcode"]
    )


# CHECK PAYMENT STATUS
@customer.get("/transactions/{transaction_id}/status", response_model=PaymentDetailResponse)
async def check_payment_status(transaction_id: int, db: AsyncSession = Depends(get_db), 
                               current_user: User = Depends(require_role("CUSTOMER"))
                               ):

    # Find transaction belonging to current customer
    query = select(PaymentTransaction).options(
       
        selectinload(PaymentTransaction.payment)
        .selectinload(Payment.transactions)).join(Payment).join(Order).where(

            PaymentTransaction.id == transaction_id,
            Order.user_id == current_user.id

        ).with_for_update()

    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment transaction not found"
        )

    payment = transaction.payment

    # Skip gateway query if transaction already completed
    if transaction.transaction_status in ["SUCCESS", "FAILED"]:
        return PaymentDetailResponse.model_validate(payment)

    # Query ZaloPay
    zalopay = ZaloPayService()

    try:
        response = await zalopay.get_payment_status(
            app_trans_id=transaction.transaction_code
        )

        print("ZaloPay payment status:", response)

    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot connect to ZaloPay"
        )

    return_code = response.get("returncode")

    # Payment successful
    if return_code == 1:

        transaction.transaction_status = "SUCCESS"
        payment.payment_status = "SUCCESS"
        payment.paid_at = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))

    # Payment failed
    elif return_code == 2:

        transaction.transaction_status = "FAILED"
        payment.payment_status = "FAILED"

    # Payment is processing
    elif return_code in (3, -49):
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=response.get(
                "returnmessage",
                "Invalid response from ZaloPay"
            )
        )

    transaction.gateway_response = json.dumps(
        response,
        ensure_ascii=False
    )

    await db.commit()

    return PaymentDetailResponse.model_validate(payment)

