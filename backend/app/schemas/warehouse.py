from pydantic import BaseModel, Field
from datetime import datetime


# CREATE WAREHOUSE
class WarehouseCreate(BaseModel):

    name: str = Field(min_length=1, max_length=150)
    address: str = Field(min_length=1)
    phone: str | None = Field(default=None, max_length=20)


# OUTPUT WAREHOUSE
class WarehouseResponse(BaseModel):

    id: int
    name: str
    address: str
    phone: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes" : True}

# UPDATE WAREHOUSE
class WarehouseUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=1, max_length=150)
    address: str | None = Field(default=None, min_length=1)
    phone: str | None = Field(default=None, max_length=20)


# UPDATE WAREHOUSE STATUS
class WarehouseStatusUpdate(BaseModel):

    is_active: bool