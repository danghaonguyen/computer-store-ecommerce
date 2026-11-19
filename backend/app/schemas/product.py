from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

# CREATED PRODUCT
class ProductCreate(BaseModel):

    category_id: int
    brand_id: int
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=200)
    description: str | None = None
    base_price: Decimal = Field(gt=0)

# OUTPUT PRODUCT
class ProductResponse(BaseModel):

    id: int
    category_id: int
    brand_id: int
    name: str
    slug: str
    description: str | None
    base_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes" : True}

# UPDATE PRODUCT
class ProductUpdate(BaseModel):

    category_id: int | None = None
    brand_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    base_price: Decimal | None = Field(default=None, gt=0)

#  UPDATE PRODUCT STATUS
class ProductStatusUpdate(BaseModel):

    is_active: bool