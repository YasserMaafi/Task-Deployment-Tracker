import asyncio
from sqlalchemy import text
from app.db.database import engine

async def test_alembic():
    async with engine.connect() as conn:
        # Check if users table exists
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_name='users'"
        ))
        tables = result.fetchall()
        
        if tables:
            print("✓ Users table exists")
        else:
            print("✗ Users table not found")
            return
        
        # Check alembic_version table
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        
        if version:
            print(f"✓ Alembic version: {version[0]}")
        else:
            print("✗ No alembic version found")
            return
        
        # Check users table structure
        result = await conn.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position"
        ))
        columns = result.fetchall()
        
        print("\n✓ Users table columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        print("\n✓ Alembic is working correctly!")

if __name__ == "__main__":
    asyncio.run(test_alembic())
