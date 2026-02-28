"""
This module defines the interfaces (ports) for persistence and caching.

`IRepository` defines the contract for a generic repository, including
methods for adding, updating, getting, deleting, searching, and listing
entities.

`ICacheRepository` defines the contract for a generic cache, including
methods for getting, checking existence, setting, and deleting cache
entries.

Both interfaces inherit from `IUnitOfWork`, which means that they are
expected to manage the transaction lifecycle.
"""
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.usecases.ports.unit_of_work_interface import IUnitOfWork


class IRepository[TInput, TResponse](IUnitOfWork, ABC):
    """Interface (port) for persistence."""

    # The use of TInput here as a parameter requires contravariance
    @abstractmethod
    async def add(self, entity: TInput) -> TResponse: ...

    @abstractmethod
    async def update(self, entity: TInput) -> TResponse: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> TResponse | None: ...

    @abstractmethod
    async def delete(self, id: UUID) -> None: ...

    @abstractmethod
    async def search(self, filter: dict[str, Any]) -> list[TResponse]: ...

    @abstractmethod
    async def list_all(self) -> list[TResponse]: ...


class ICacheRepository[TInput, TResponse](IUnitOfWork, ABC):
    """Interface (port) for cache."""

    @abstractmethod
    async def get(self, key: str) -> TResponse | None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def set(
        self, key: str, value: TInput, expire: int | None = None
    ) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...
