"""
SQLAlchemy implementation of the customer repository.

This module provides a concrete implementation of the `IDBCustomerRepository`
interface using SQLAlchemy for data persistence. It handles the mapping
between the `Customer` domain entity and the `CustomerModel` ORM model.
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

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
    SQLAlchemyRepository[Customer, CustomerModel], IDBCustomerRepository
):
    """
    SQLAlchemy-based repository for customers.

    This class manages the persistence of `Customer` entities using an
    SQLAlchemy `AsyncSession`. It acts as a Unit of Work, handling the
    session lifecycle.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an active database session.

        Args:
            session: An `AsyncSession` from SQLAlchemy to interact with the
                database.
        """
        super().__init__(session, CustomerModel)

    async def update(self, entity: Customer) -> Customer:
        """
        Updates an existing customer in the database.

        Args:
            entity: The `Customer` entity with updated data.

        Returns:
            The updated `Customer` entity.
        """
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == entity.id)
            .values(
                name=entity.name,
                email=entity.email.value,
                updated_at=entity.updated_at,
            )
        )
        await self.session.execute(stmt)
        return entity

    async def exists_by_email(self, email: str) -> bool:
        """
        Checks if a customer with the given email already exists.

        Args:
            email: The email address to check.

        Returns:
            True if a customer with the email exists, False otherwise.
        """
        stmt = select(self.model_class).where(self.model_class.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    def _to_model(self, entity: Customer) -> CustomerModel:
        """
        Converts a `Customer` domain entity to a `CustomerModel` ORM object.

        Args:
            entity: The `Customer` domain entity.

        Returns:
            The corresponding `CustomerModel` ORM object.
        """
        return CustomerModel(
            id=entity.id,
            name=entity.name,
            email=entity.email.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _to_entity(self, model: CustomerModel) -> Customer:
        """
        Converts a `CustomerModel` ORM object to a `Customer` domain entity.

        Args:
            model: The `CustomerModel` ORM object.

        Returns:
            The corresponding `Customer` domain entity.
        """
        return Customer(
            id=model.id,
            name=model.name,
            email=Email(model.email),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
