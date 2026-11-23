from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.database import get_db
from app.router import (
    auth, 
    users, 
    categories,
    products,
    product_variants,
    product_images,
    product_attributes,
    product_catalog,
    carts,
    wishlist,
    warehouses,
    inventories,
    stock_movements,
    suppliers,
    orders,
    payments
    )
from app.router import brands


app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)

app.include_router(categories.router)
app.include_router(brands.router)

app.include_router(products.router)
app.include_router(product_variants.router)
app.include_router(product_images.router)
app.include_router(product_attributes.router)

app.include_router(product_catalog.router)
app.include_router(carts.router)
app.include_router(wishlist.router)

app.include_router(warehouses.router)
app.include_router(inventories.router)
app.include_router(stock_movements.router)
app.include_router(suppliers.router)

app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/db-check")
async def testdb(db: AsyncSession = Depends(get_db)):

    result = await db.execute(text("SELECT 1"))

    return {
        "status": "success",
        "message": "Kết nối PostgreSQL thành công",
        "result": result.scalar_one()
    }