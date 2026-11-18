from pydantic import BaseModel, Field
from datetime import datetime

# CREATE BRAND
class BrandCreate(BaseModel):

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)


# OUTPUT BRAND
class BrandResponse(BaseModel):

    id: int
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes" : True}


# UPDATE BRAND
class BrandUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)


# UPDATE BRAND STATUS
class BrandStatusUpdate(BaseModel):

    is_active: bool

    
