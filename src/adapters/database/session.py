"""
Database Session Setup.

This script is responsible for setting up the database session for the
application. It creates an asynchronous SQLAlchemy engine, configures a
session factory, and provides a dependency injection utility (`get_session`)
to supply sessions to other parts of the application, such as Unit of Work
implementations or FastAPI dependencies.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings

# 1. Create an asynchronous engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ECHO_SQL,
)

# 2. Configure the session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# 3. Dependency Injection (for use in UnitOfWork or FastAPI)
async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency injector that provides a SQLAlchemy `AsyncSession`.

    It is designed to be used with FastAPI's dependency injection system or
    as part of a Unit of Work pattern. It ensures that a session is created
    and properly closed after use.

    Yields:
        An `AsyncSession` instance.
    """
    async with async_session_factory() as session:
        yield session
