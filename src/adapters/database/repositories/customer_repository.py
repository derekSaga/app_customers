
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapters.database.repositories.base_repository import (
    SQLAlchemyRepository,
)
from src.domain.entities.customer import Customer
from src.domain.models.customer import CustomerModel
from src.domain.value_objects.email import Email
from src.usecases.v1.customers.ports.customer_repositories import (
    IDBCustomerRepository,
)


class SQLAlchemyCustomerRepository(
    SQLAlchemyRepository[Customer, CustomerModel],
    IDBCustomerRepository
):
    """
    Implementação do Repositório de Clientes usando SQLAlchemy.
    Gerencia a persistência e o ciclo de vida da sessão (Unit of Work).
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory, CustomerModel)

    async def update(self, entity: Customer) -> Customer:
        stmt = (
            update(CustomerModel)
            .where(CustomerModel.id == entity.id)
            .values(
                name=entity.name,
                email=entity.email.value,
                updated_at=entity.updated_at,
            )
        )
        await self.session.execute(stmt)
        return entity

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(CustomerModel).where(CustomerModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    def _to_model(self, entity: Customer) -> CustomerModel:
        return CustomerModel(
            id=entity.id,
            name=entity.name,
            email=entity.email.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _to_entity(self, model: CustomerModel) -> Customer:
        return Customer(
            id=model.id,
            name=model.name,
            email=Email(model.email),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )