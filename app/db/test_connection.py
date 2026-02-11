import asyncio
from app.db.database import engine

async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: print("Connected to DB!"))

asyncio.run(test_db())
