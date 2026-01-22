from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from src.domain.entities.customer import Customer
from src.usecases.ports.base_publisher import BasePublisher
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


class ICustomerControlCache(Protocol):
    """
    Interface para interação com cache de controle (ex: Locks, Idempotência).
    Difere do repositório de entidade por lidar com chaves/valores arbitrários.
    """

    async def exists(self, key: str) -> bool: ...
    async def set(
        self, key: str, value: str, expire: int | None = None
    ) -> None: ...


class ICustomerMessagePublisher(BasePublisher[Customer], ABC):
    """Interface para publicação de mensagens de Cliente."""

    @abstractmethod
    async def publish_customer_creation(self, customer: Customer) -> None: ...
