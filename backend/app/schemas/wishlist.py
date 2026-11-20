from pydantic import BaseModel
from datetime import datetime
from app.schemas.product_variant import ProductVariantResponse

# ADD PRODUCT IN WISHLIST
class WishlistCreate(BaseModel):

    product_variant_id: int

# OUTPUT WISHTLIST
class WishlistResponse(BaseModel):

    id: int
    user_id: int
    product_variant_id: int
    created_at: datetime
    product_variant: ProductVariantResponse

    model_config = {"from_attributes" : True}

