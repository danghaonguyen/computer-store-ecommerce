from decimal import Decimal
from pydantic import BaseModel, Field

# ADD PRODUCT VARIANT
class ProductVariantCreate(BaseModel):

    sku: str | None = Field(min_length=1, max_length=100)
    variant_name: str = Field(min_length=1, max_length=150)
    price: Decimal = Field(gt=0)
    compare_at_price: Decimal | None = Field(default=None, gt=0)


# OUTPUT PRODUCT VARIANT
class ProductVariantResponse(BaseModel):

    id: int
    product_id: int
    sku: str
    variant_name: str
    price: Decimal
    compare_at_price: Decimal | None
    is_active: bool

    model_config = {"from_attributes" : True}

# UPDATE PRODUCT VARIANT
class ProductVariantUpdate(BaseModel):

    sku: str | None = Field(default=None, min_length=1, max_length=100)
    variant_name: str | None = Field(default=None, min_length=1, max_length=150)
    price: Decimal | None = Field(default=None, gt=0)
    compare_at_price: Decimal | None = Field(default=None, gt=0)

# UPDATE PRODUCT VARIANT ID
class ProductVariantStatusUpdate(BaseModel):

    is_active: bool