from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.product_variant import ProductVariantResponse


# ADD CART ITEMS
class CartItemCreate(BaseModel):

    product_variant_id: int
    quantity: int = Field(default=1, gt=0)


# UPDATE CART ITEMS
class CartItemUpdate(BaseModel):

    quantity: int = Field(gt=0)


# OUTPUT CART ITEMS
class CartItemResponse(BaseModel):

    id: int
    cart_id: int
    product_variant_id: int
    quantity: int
    added_at: datetime
    product_variant: ProductVariantResponse

    model_config = {"from_attributes": True}


# OUTPUT CART
class CartResponse(BaseModel):

    id: int
    user_id: int
    items: list[CartItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes" : True}

# UPDATE QUANTITY CART ITEM
class CartItemUpdate(BaseModel):

    quantity: int = Field(gt=0)

    