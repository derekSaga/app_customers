from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.usecases.ports.unit_of_work import IUnitOfWork


class IRepository[TInput, TResponse](IUnitOfWork, ABC):
    """Interface (port) para persistência."""

    # O uso de TInput aqui como parâmetro exige contravariância
    @abstractmethod
    def add(self, entity: TInput) -> TResponse: ...

    @abstractmethod
    def update(self, entity: TInput) -> TResponse: ...

    @abstractmethod
    def get_by_id(self, id: UUID) -> TResponse | None: ...

    @abstractmethod
    def delete(self, id: UUID) -> None: ...

    @abstractmethod
    def search(self, filter: dict[str, Any]) -> list[TResponse]: ...

    @abstractmethod
    def list_all(self) -> list[TResponse]: ...


class ICacheRepository[TInput, TResponse](IUnitOfWork, ABC):
    """Interface (port) para cache."""

    @abstractmethod
    def get(self, key: str) -> TResponse | None: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def set(
        self, key: str, value: TInput, expire: int | None = None
    ) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...
