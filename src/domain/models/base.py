"""
This module defines the base class for all SQLAlchemy models in the
application.

It includes support for `AsyncAttrs` for asynchronous lazy loading and defines
common columns like `id`, `created_at`, and `updated_at`. It also sets the
default database schema based on the application settings.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Includes support for `AsyncAttrs` for asynchronous lazy loading.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    metadata = MetaData(schema=settings.DATABASE_SCHEMA)
