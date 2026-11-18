from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.database import get_db
from app.router import (
    auth, 
    brand, 
    users, 
    categories
    )

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(brand.router)




@app.get("/db-check")
async def testdb(db: AsyncSession = Depends(get_db)):

    result = await db.execute(text("SELECT 1"))

    return {
        "status": "success",
        "message": "Kết nối PostgreSQL thành công",
        "result": result.scalar_one()
    }