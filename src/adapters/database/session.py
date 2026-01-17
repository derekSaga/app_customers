from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings

# 1. Criação da Engine Assíncrona
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ECHO_SQL,
)

# 2. Configuração da Factory de Sessões
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# 3. Dependency Injection (para usar no UnitOfWork ou FastAPI)
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
