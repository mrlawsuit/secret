from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# from config import DB_URL
from .config import DB_URL
from .models import Base

engine = create_async_engine(DB_URL)

async_session = async_sessionmaker(engine)


def create_tables(sync_engine):
    Base.metadata.create_all(bind=sync_engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(create_tables)


async def dispose_engine():
    await engine.dispose()

if __name__ == '__main__':
    print('done')