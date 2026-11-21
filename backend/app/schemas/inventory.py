from pydantic import BaseModel, Field
from datetime import datetime


# CREATED INVENTORY
class InventoryCreate(BaseModel):
    
    warehouse_id: int = Field(gt=0)
    product_variant_id: int = Field(gt=0)




# OUTPUT INVENTORY
class InventoryResponse(BaseModel):

    id: int
    warehouse_id: int
    product_variant_id: int
    quantity: int
    reserved_quantity: int
    updated_at: datetime


    model_config = {"from_attributes" : True}



    