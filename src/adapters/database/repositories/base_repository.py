"""
This module provides a generic base 
implementation of a repository using SQLAlchemy.

It manages the persistence and session lifecycle (Unit of Work).
"""
from abc import abstractmethod
from types import TracebackType
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.base import Base
from src.usecases.ports.repositories_interface import IRepository

TModel = TypeVar("TModel", bound=Base)
TDomainEntity = TypeVar("TDomainEntity")


class SQLAlchemyRepository[TDomainEntity, TModel: Base](
    IRepository[TDomainEntity, TDomainEntity]
):
    """
    Generic base implementation of a Repository using SQLAlchemy.

    Manages persistence and session lifecycle (Unit of Work).
    """

    def __init__(
        self,
        session: AsyncSession,
        model_class: type[TModel],
    ):
        """
        Initializes the repository with a session and a model class.

        Args:
            session: The SQLAlchemy async session.
            model_class: The SQLAlchemy model class.
        """
        self.session = session
        self.model_class = model_class

    async def __aenter__(
        self: "SQLAlchemyRepository[TDomainEntity, TModel]",
    ) -> "SQLAlchemyRepository[TDomainEntity, TModel]":
        """
        Enter the context manager.

        Returns:
            The repository instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the context manager, committing or rolling back the transaction.

        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The traceback.
        """
        if exc_type:
            await self.rollback()
            return

        await self.commit()

    async def commit(self) -> None:
        """Commits the transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rolls back the transaction."""
        await self.session.rollback()

    async def add(self, entity: TDomainEntity) -> TDomainEntity:
        """
        Adds a new entity to the database.

        Args:
            entity: The domain entity to add.

        Returns:
            The added domain entity.
        """
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: TDomainEntity) -> TDomainEntity:
        """
        Updates an existing entity.

        Args:
            entity: The domain entity to update.

        Returns:
            The updated domain entity.
        """
        model = self._to_model(entity)
        await self.session.merge(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, id: UUID) -> TDomainEntity | None:
        """
        Retrieves an entity by its ID.

        Args:
            id: The ID of the entity to retrieve.

        Returns:
            The domain entity if found, otherwise None.
        """
        stmt = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def delete(self, id: UUID) -> None:
        """
        Deletes an entity by its ID.

        Args:
            id: The ID of the entity to delete.
        """
        stmt = delete(self.model_class).where(self.model_class.id == id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def search(self, filter: dict[str, Any]) -> list[TDomainEntity]:
        """
        Searches for entities based on a filter.

        Args:
            filter: A dictionary of filters to apply.

        Returns:
            A list of domain entities that match the filter.
        """
        stmt = select(self.model_class)
        for key, value in filter.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_all(self) -> list[TDomainEntity]:
        """
        Retrieves all entities.

        Returns:
            A list of all domain entities.
        """
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @abstractmethod
    def _to_model(self, entity: TDomainEntity) -> TModel:
        """
        Maps a domain entity to a database model.

        Args:
            entity: The domain entity to map.

        Returns:
            The database model.
        """
        ...

    @abstractmethod
    def _to_entity(self, model: TModel) -> TDomainEntity:
        """
        Maps a database model to a domain entity.

        Args:
            model: The database model to map.

        Returns:
            The domain entity.
        """
        ...
