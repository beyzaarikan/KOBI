import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# We will use SQLite for the hackathon demo if Postgres is not provided, 
# but the plan specified Postgres. For immediate local dev without needing docker, 
# let's use async sqlite, and swap to postgres via env var.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kobi_app.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
