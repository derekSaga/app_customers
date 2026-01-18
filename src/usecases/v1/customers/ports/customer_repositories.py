from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.customer import Customer
from src.usecases.ports.repositories import ICacheRepository, IRepository


class IDBCustomerRepository(IRepository[Customer, Customer], ABC):
    """
    Porta de Saída (Driven Port):
    Define as operações de banco de dados necessárias, mas não como fazê-las.
    Herda add, update, delete, get_by_id de IRepository.
    """

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...


class ICacheCustomerRepository(ICacheRepository[Customer, Customer], ABC):
    """
    Porta de Saída (Driven Port):
    Define as operações de cache específicas para o domínio Customer.
    Herda operações básicas (set, get, exists) de ICacheRepository.
    """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Customer | None: ...
