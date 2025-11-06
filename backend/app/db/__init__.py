from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_database_url


class Base(DeclarativeBase):
    pass


def create_async_db_engine():
    return create_async_engine(
        get_database_url(),
        pool_pre_ping=True,
        echo=False,
    )


def get_async_session_local(engine=None):
    engine = engine or create_async_db_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


engine = create_async_db_engine()
AsyncSessionLocal = get_async_session_local(engine)


# Dependency for getting async database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
