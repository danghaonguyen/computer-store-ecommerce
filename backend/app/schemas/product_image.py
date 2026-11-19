from pydantic import BaseModel, Field

# ADD PRODUCT IMAGES
class ProductImageCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=255)
    is_primary: bool = False
    sort_order: int = 0

# OUTPUT PRODUCT IMAGES
class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    alt_text: str | None
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


# UPDATA PRODUCT IMAGES
class ProductImageUpdate(BaseModel):

    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=255)
    is_primary: bool | None = None
    sort_order: int | None = None

    