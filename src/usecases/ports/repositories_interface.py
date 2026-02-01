from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.usecases.ports.unit_of_work_interface import IUnitOfWork


class IRepository[TInput, TResponse](IUnitOfWork, ABC):
    """Interface (port) para persistência."""

    # O uso de TInput aqui como parâmetro exige contravariância
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
    """Interface (port) para cache."""

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
