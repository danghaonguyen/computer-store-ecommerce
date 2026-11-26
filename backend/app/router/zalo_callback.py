import json
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db

from app.model_database.payments.payment_transaction import PaymentTransaction
from app.schemas.payment import ZaloPayCallbackRequest

from app.services.zalopay_service import ZaloPayService

callback_router = APIRouter(prefix="/payments", tags=["Payment Callback"])

# ZALOPAY CALLBACK
@callback_router.post("/callback")
async def zalopay_callback(callback_data: ZaloPayCallbackRequest,
                           db: AsyncSession = Depends(get_db)):
    
    zalopay = ZaloPayService()

    # Verify callback signature
    try:
        callback_data = callback_data.model_dump()

        data = zalopay.verify_callback(callback_data)

    except (ValueError, TypeError, json.JSONDecodeError):
        data = None

    if data is None:
        return {
            "return_code": 2,
            "return_message": "Invalid MAC"
        }

    # Only handle payment order callbacks
    if callback_data.get("type") != 1:
        return {
            "return_code": 2,
            "return_message": "Invalid callback type"
        }

    # Verify app ID
    try:
        if int(data.get("app_id")) != int(zalopay.app_id):
            return {
                "return_code": 2,
                "return_message": "Invalid app ID"
            }
    except (ValueError, TypeError):
        return {
            "return_code": 2,
            "return_message": "Invalid app ID"
        }

    app_trans_id = data.get("app_trans_id")

    if not app_trans_id:
        return {
            "return_code": 2,
            "return_message": "Missing transaction ID"
        }

    # Find payment transaction
    query = (
        select(PaymentTransaction)
        .options(selectinload(PaymentTransaction.payment))
        .where(PaymentTransaction.transaction_code == app_trans_id)
        .with_for_update()
    )

    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if transaction is None:
        return {
            "return_code": 0,
            "return_message": "Transaction not found"
        }

    payment = transaction.payment

    # Verify transaction amount
    try:
        callback_amount = Decimal(str(data.get("amount")))
    except (ValueError, TypeError):
        return {
            "return_code": 2,
            "return_message": "Invalid amount"
        }

    print("Callback amount:", repr(callback_amount))
    print("Transaction amount:", repr(transaction.amount))
    print("Payment amount:", repr(payment.amount))

    print("Callback == Transaction:", callback_amount == transaction.amount)
    print("Callback == Payment:", callback_amount == payment.amount)

    if (
        callback_amount != transaction.amount
        or callback_amount != payment.amount
    ):
        return {
            "return_code": 2,
            "return_message": "Amount mismatch"
        }

    # Handle duplicate callback
    if transaction.transaction_status == "SUCCESS":
        return {
            "return_code": 1,
            "return_message": "success"
        }

    # Do not overwrite a failed transaction
    if transaction.transaction_status == "FAILED":
        return {
            "return_code": 2,
            "return_message": "Transaction already failed"
        }

    # Update payment and transaction
    transaction.transaction_status = "SUCCESS"
    payment.payment_status = "SUCCESS"
    payment.paid_at = datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    )

    transaction.gateway_response = json.dumps(
        callback_data,
        ensure_ascii=False
    )

    await db.commit()

    return {
        "return_code": 1,
        "return_message": "success"
    }
