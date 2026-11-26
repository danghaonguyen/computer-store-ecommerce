from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.database import get_db
from app.router import auth, zalo_callback
 
from app.router.admin import (
    brands, 
    categories, 
    inventories, 
    product_attributes, 
    product_images, 
    product_variants, 
    products, 
    shipments, 
    stock_movements, 
    suppliers, 
    users, 
    warehouses,
    orders,
    payments
)

from app.router.customer import (
    carts, 
    set_orders, 
    product_catalog, 
    wishlist,
    orders_shipment,
    view_shipments,
    use_coupons,
    use_payments
)


app = FastAPI()

# AUTHORIZATION
app.include_router(auth.router)

# ADMIN MANAGEMENT ==========================================

# User Management
app.include_router(users.admin)

# Brand & Category Management
app.include_router(brands.admin)
app.include_router(categories.admin)

# Product management
app.include_router(products.admin)
app.include_router(product_variants.admin)
app.include_router(product_attributes.admin)
app.include_router(product_images.admin)

# Warhouses & Inventory & Stock Movement & Supplier Management
app.include_router(warehouses.admin)
app.include_router(inventories.admin)
app.include_router(stock_movements.admin)
app.include_router(suppliers.admin)

# Order & Payment & Shipment Management
app.include_router(orders.admin)
app.include_router(payments.admin)
app.include_router(shipments.admin)

# CUSTOMER ==========================================

# Cart & Set Order Management
app.include_router(carts.customer)
app.include_router(set_orders.customer)

# View Product Catalog
app.include_router(product_catalog.customer)

# Wilist & Order Shipment Management
app.include_router(wishlist.customer)
app.include_router(orders_shipment.customer)
app.include_router(view_shipments.customer)

# Use Method Payment & Coupons
app.include_router(use_coupons.customer)
app.include_router(use_payments.customer)

# ZALOPAY CALLBACK
app.include_router(zalo_callback.callback_router)


# Test Database
@app.get("/db-check")
async def testdb(db: AsyncSession = Depends(get_db)):

    result = await db.execute(text("SELECT 1"))

    return {
        "status": "success",
        "message": "Kết nối PostgreSQL thành công",
        "result": result.scalar_one()
    }