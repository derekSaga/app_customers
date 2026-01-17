from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.customer import Customer
from src.usecases.ports.repositories import IRepository


class ICustomerRepository(IRepository[Customer, Customer], ABC):
    """
    Porta de Saída (Driven Port):
    Define as operações de banco de dados necessárias, mas não como fazê-las.
    """

    @abstractmethod
    def add(self, entity: Customer) -> Customer: ...

    @abstractmethod
    def get_by_id(self, id: UUID) -> Customer: ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool: ...
