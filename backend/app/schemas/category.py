from pydantic import BaseModel, Field
from datetime import datetime


# CREATE CATOGRY
class CategoryCreate(BaseModel):

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None


# OUTPUT CATEGORY
class CategoryResponse(BaseModel):

    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    parent_id: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes" : True}


# UPDATE CATEGORY
class CategoryUpdate(BaseModel):

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None


# UPDATE STATUS CATEGORY
class CategoryStatusUpdate(BaseModel):

    is_active: bool
