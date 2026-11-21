from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# CREATE SUPPLIER
class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    contact_person: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = None


# UPDATE SUPPLIER
class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    contact_person: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = None
    is_active: bool | None = None


# RESPONSE SUPPLIER
class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)