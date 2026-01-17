from uuid import UUID

from src.domain.entities.customer import Customer
from src.usecases.ports.repositories import IRepository


class ICustomerRepository(IRepository[Customer, Customer]):
    """
    Porta de Saída (Driven Port):
    Define as operações de banco de dados necessárias, mas não como fazê-las.
    """

    def add(self, entity: Customer) -> None: ...

    def get_by_id(self, id: UUID) -> Customer | None: ...
