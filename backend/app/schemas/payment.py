
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentTransactionResponse(BaseModel):
    id: int
    transaction_code: str | None
    transaction_type: str
    transaction_status: str
    amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# OUTPUT RESPONSE
class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: str
    payment_status: str
    amount: Decimal
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# OUTPUT DETAIL PAYMENT RESPONSE
class PaymentDetailResponse(PaymentResponse):

    transactions: list[PaymentTransactionResponse] = Field(default_factory=list)


class PaymentCheckoutResponse(BaseModel):
    payment_id: int
    transaction_id: int
    transaction_code: str
    payment_status: str
    amount: Decimal
    qr_code: str


class ZaloPayCallbackRequest(BaseModel):
    data: str
    mac: str
    type: int