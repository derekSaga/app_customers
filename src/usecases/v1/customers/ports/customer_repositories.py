from abc import ABC, abstractmethod
from uuid import UUID

from src.adapters.publishers.base_publisher import BasePublisher
from src.domain.entities.customer import Customer
from src.usecases.ports.repositories_interface import (
    ICacheRepository,
    IRepository,
)


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


class ICustomerControlCache(ICacheRepository[str, str], ABC):
    """
    Interface para interação com cache de controle (ex: Locks, Idempotência).
    Herda de ICacheRepository para aproveitar o contrato de UnitOfWork.
    """

    pass


class ICustomerMessagePublisher(BasePublisher[Customer], ABC):
    """Interface para publicação de mensagens de Cliente."""

    @abstractmethod
    async def publish_customer_creation(self, customer: Customer) -> None: ...
