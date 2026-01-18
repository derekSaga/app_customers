from abc import abstractmethod
from types import TracebackType
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.models.base import Base
from src.usecases.ports.repositories import IRepository

TModel = TypeVar("TModel", bound=Base)
TDomainEntity = TypeVar("TDomainEntity")


class SQLAlchemyRepository[TDomainEntity, TModel: Base](
    IRepository[TDomainEntity, TDomainEntity]
):
    """
    Implementação base genérica de Repositório usando SQLAlchemy.
    Gerencia a persistência e o ciclo de vida da sessão (Unit of Work).
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        model_class: type[TModel],
    ):
        self.session_factory = session_factory
        self.model_class = model_class
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError(
                "Sessão não inicializada. Use 'async with repository' "
                "ou inicialize manualmente."
            )
        return self._session

    async def __aenter__(
        self: "SQLAlchemyRepository[TDomainEntity, TModel]",
    ) -> "SQLAlchemyRepository[TDomainEntity, TModel]":
        self._session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            if exc_type:
                await self.rollback()
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def add(self, entity: TDomainEntity) -> TDomainEntity:
        model = self._to_model(entity)
        self.session.add(model)
        return entity

    async def update(self, entity: TDomainEntity) -> TDomainEntity:
        model = self._to_model(entity)
        await self.session.merge(model)
        return entity

    async def get_by_id(self, id: UUID) -> TDomainEntity | None:
        stmt = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def delete(self, id: UUID) -> None:
        stmt = delete(self.model_class).where(self.model_class.id == id)
        await self.session.execute(stmt)

    async def search(self, filter: dict[str, Any]) -> list[TDomainEntity]:
        stmt = select(self.model_class)
        for key, value in filter.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_all(self) -> list[TDomainEntity]:
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @abstractmethod
    def _to_model(self, entity: TDomainEntity) -> TModel:
        """Mapeia Entity -> DB Model"""
        ...

    @abstractmethod
    def _to_entity(self, model: TModel) -> TDomainEntity:
        """Mapeia DB Model -> Entity"""
        ...