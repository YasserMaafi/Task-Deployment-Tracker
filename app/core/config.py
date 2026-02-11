import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://tdt_user:tdt_pass@localhost:5432/tdt_db"
)
