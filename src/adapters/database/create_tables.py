"""
Database Table Creation Script.

This script is responsible for creating database tables based on the SQLAlchemy
models defined in the application. It connects to the database using the
engine from `src.adapters.database.session`, creates the specified schema
if it doesn't exist, and then creates all tables that inherit from the `Base`
model.

This is a crucial utility for setting up the database schema before running
the application for the first time.

It is important to import all SQLAlchemy models here so they are registered
with `Base.metadata`.

The script can be run directly to perform the table creation.
"""
import asyncio

from loguru import logger
from sqlalchemy import text

from src.adapters.database.session import engine
from src.domain.models.base import Base
from src.domain.models.customer import CustomerModel  # noqa: F401

# ----------------------------------------------------------------------------
# IMPORTANT: Import your models here!
# SQLAlchemy needs the model classes to be loaded into memory so they can be
# registered with Base.metadata.
#
# Example (adjust the path according to where you defined your SQLAlchemy model):
# from src.adapters.database.models.customer import CustomerModel
# ----------------------------------------------------------------------------


async def create_tables() -> None:
    """
    Creates all tables defined in models that inherit from Base.
    """
    logger.info("Starting table creation...")

    async with engine.begin() as conn:
        if Base.metadata.schema:
            logger.info(
                f"Creating schema '{Base.metadata.schema}' if it does not exist..."
            )
            await conn.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}")
            )

        await conn.run_sync(Base.metadata.create_all)

    logger.info("Tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())
