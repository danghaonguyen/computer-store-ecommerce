from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Literal

ShippingStatus = Literal[
    "PENDING",
    "PREPARING",
    "SHIPPED",
    "IN_TRANSIT",
    "DELIVERED",
    "FAILED",
    "RETURNED"
]


# CREATE SHIPMENT
class ShipmentCreate(BaseModel):
    order_id: int = Field(gt=0)
    shipping_provider: str | None = None
    tracking_number: str | None = None
    shipping_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    note: str | None = None


# UPDATE SHIPMENT
class ShipmentUpdate(BaseModel):
    shipping_provider: str | None = None
    tracking_number: str | None = None
    shipping_status: ShippingStatus | None = None
    shipping_fee: Decimal | None = Field(default=None, ge=0)
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    note: str | None = None


# OUTPUT SHIPMENT
class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    shipping_provider: str | None
    tracking_number: str | None
    shipping_status: ShippingStatus
    shipping_fee: Decimal
    shipped_at: datetime | None
    delivered_at: datetime | None
    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes" : True}
