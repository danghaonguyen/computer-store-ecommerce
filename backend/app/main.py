from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.database import get_db

app = FastAPI()


@app.get("/db-check")
async def testdb(db: AsyncSession = Depends(get_db)):

    result = await db.execute(text("SELECT 1"))

    return {
        "status": "success",
        "message": "Kết nối PostgreSQL thành công",
        "result": result.scalar_one()
    }