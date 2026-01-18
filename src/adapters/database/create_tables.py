import asyncio

from loguru import logger
from sqlalchemy import text

from src.adapters.database.session import engine
from src.domain.models.base import Base
from src.domain.models.customer import CustomerModel  # noqa: F401

# ----------------------------------------------------------------------------
# IMPORTANTE: Importe seus modelos aqui!
# O SQLAlchemy precisa que as classes dos modelos sejam carregadas em memória
# para que elas sejam registradas no Base.metadata.
#
# Exemplo (ajuste o caminho conforme onde você definiu seu modelo SQLAlchemy):
# from src.adapters.database.models.customer import CustomerModel
# ----------------------------------------------------------------------------


async def create_tables() -> None:
    """
    Cria todas as tabelas definidas nos modelos que herdam de Base.
    """
    logger.info("Iniciando criação de tabelas...")

    async with engine.begin() as conn:
        if Base.metadata.schema:
            logger.info(
                f"Criando schema '{Base.metadata.schema}' se não existir..."
            )
            await conn.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}")
            )

        await conn.run_sync(Base.metadata.create_all)

    logger.info("Tabelas criadas com sucesso!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())
