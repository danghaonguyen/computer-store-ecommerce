from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


# ADD STOCK MOVEMENT
class StockMovementCreate(BaseModel):

    inventory_id: int
    supplier_id: int | None = None
    movement_type: Literal[
        "IN",
        "OUT",
        "ADJUSTMENT_IN",
        "ADJUSTMENT_OUT"
    ]
    quantity: int = Field(gt=0)
    note: str | None = None



# OUTPUT STOCK MOVMENT
class StockMovementResponse(BaseModel):

    id: int
    inventory_id: int
    supplier_id: int | None
    movement_type: str
    quantity: int
    note: str | None
    created_at: datetime

    model_config = {"from_attributes" : True}