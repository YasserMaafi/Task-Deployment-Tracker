import asyncio
from sqlalchemy.future import select
from app.db.database import async_session
from app.models.user import User
from app.core.security import hash_password


async def create_admin():
    async with async_session() as db:
        # Check if admin already exists
        result = await db.execute(select(User).where(User.role == "admin"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin already exists.")
            return

        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin"
        )

        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

        print("Admin created successfully.")


if __name__ == "__main__":
    asyncio.run(create_admin())
