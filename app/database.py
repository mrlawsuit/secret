from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DB_URL

engine = create_async_engine(DB_URL)

async_session = async_sessionmaker(engine)
