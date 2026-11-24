
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, model_validator

# COUPON CREATE
class CouponCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None

    discount_type: Literal["PERCENTAGE", "FIXED"]
    discount_value: Decimal = Field(gt=0)

    minimum_order_amount: Decimal = Field(default=0, ge=0)
    maximum_discount_amount: Decimal | None = Field(default=None, gt=0)

    usage_limit: int | None = Field(default=None, gt=0)
    usage_limit_per_user: int = Field(default=1, gt=0)

    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def validate_coupon(self):
        if self.discount_type == "PERCENTAGE" and self.discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100")

        if self.end_at <= self.start_at:
            raise ValueError("End date mush after start date")

        return self

# OUTPUT COUPON
class CouponResponse(BaseModel):
    id: int
    code: str
    description: str | None

    discount_type: str
    discount_value: Decimal

    minimum_order_amount: Decimal
    maximum_discount_amount: Decimal | None

    usage_limit: int | None
    usage_limit_per_user: int
    used_count: int

    start_at: datetime
    end_at: datetime
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes" : True}


# COUPON UPDATE
class CouponUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None

    discount_type: Literal["PERCENTAGE", "FIXED"] | None = None
    discount_value: Decimal | None = Field(default=None, gt=0)

    minimum_order_amount: Decimal | None = Field(default=None, ge=0)
    maximum_discount_amount: Decimal | None = Field(default=None, gt=0)

    usage_limit: int | None = Field(default=None, gt=0)
    usage_limit_per_user: int | None = Field(default=None, gt=0)

    start_at: datetime | None = None
    end_at: datetime | None = None

    @model_validator(mode="after")
    def validate_coupon(self):
        if self.discount_type == "PERCENTAGE" and self.discount_value is not None:
            if self.discount_value > 100:
                raise ValueError("Percentage discount cannot exceed 100")

        if self.start_at is not None and self.end_at is not None:
            if self.end_at <= self.start_at:
                raise ValueError("End date must be after start date")

        return self


# COUPON STATUS
class CouponUpdateStatus(BaseModel):

    is_active: bool



# CUSTOMER
# COUPON VALIDATE
class CouponValidate(BaseModel):

    code: str = Field(min_length=1, max_length=50)
    subtotal: Decimal = Field(gt=0)

# COUPON VALIDATE RESPONSE
class CouponValidateResponse(BaseModel):
    code: str
    discount_type: str
    discount_value: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    total_after_discount: Decimal