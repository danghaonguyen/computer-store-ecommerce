from pydantic import BaseModel, Field

# ADD PRODUCT ATTRIBUTE
class ProductAttributeCreate(BaseModel):
    attribute_name: str = Field(min_length=1, max_length=100)
    attribute_value: str = Field(min_length=1)

# OUTPUT PRODUCT ATTRIBUTE
class ProductAttributeResponse(BaseModel):
    id: int
    product_id: int
    attribute_name: str
    attribute_value: str

    model_config = {"from_attributes": True}

# UPDATE PRODUCT ATTRIBUTE
class ProductAttributeUpdate(BaseModel):
    attribute_name: str | None = Field(default=None, min_length=1, max_length=100)
    attribute_value: str | None = Field(default=None, min_length=1)