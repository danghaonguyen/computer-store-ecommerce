from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Literal

# CREATE ORDER
class OrderCreate(BaseModel):

    recipient_name: str = Field(min_length=1, max_length=100)
    recipient_phone: str = Field(min_length=10, max_length=15)
    shipping_province: str = Field(min_length=1, max_length=100)
    shipping_district: str = Field(min_length=1, max_length=100)
    shipping_ward: str = Field(min_length=1, max_length=100)
    shipping_address: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=255)

    
    coupon_code: str | None = Field(default=None, min_length=1, max_length=50)


# OUTPUT ORDER
class OrderResponse(BaseModel):

    id: int
    order_number: str
    user_id: int
    status: str

    recipient_name: str
    recipient_phone: str

    shipping_province: str
    shipping_district: str
    shipping_ward: str
    shipping_address: str

    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal

    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# OUTPUT ORDER ITEM
class OrderItemResponse(BaseModel):

    id: int
    order_id: int

    product_variant_id: int
    product_name: str
    variant_name: str | None
    sku: str

    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {"from_attributes" : True}

# OUTPUT ORDER DETAIL
class OrderDetailResponse(OrderResponse):

    items: list[OrderItemResponse]


# UPDATE ORDER STATUS FOR ADMIN
class OrderStatusUpdate(BaseModel):
    
    status: Literal[
        "CONFIRMED",
        "PROCESSING",
        "SHIPPED",
        "DELIVERED"
    ]
    note: str | None = None



# OUTPUT ORDER STATUS HISTORY
class OrderStatusHistoryResponse(BaseModel):

    id: int
    order_id: int
    changed_by: int | None
    status: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}