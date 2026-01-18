from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    Inclui suporte a AsyncAttrs para carregamento
    preguiçoso (lazy loading) assíncrono.
    """
    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    metadata = MetaData(schema=settings.DATABASE_SCHEMA)
