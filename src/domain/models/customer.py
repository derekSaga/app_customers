"""
This module defines the `CustomerModel`, which is the SQLAlchemy ORM model
for the `Customer` entity.

It maps the `Customer` entity to the `customers` table in the database and
provides methods for converting between the domain entity and the
persistence model.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.customer import Customer
from src.domain.models.base import Base
from src.domain.value_objects.email import Email


class CustomerModel(Base):
    """The SQLAlchemy ORM model for the `Customer` entity."""

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    def to_entity(self) -> Customer:
        """Converts the persistence model to the domain entity."""
        # Assuming the Customer constructor accepts id, name, and the Email VO
        return Customer(
            id=self.id,
            name=self.name,
            email=Email(self.email),
            updated_at=self.updated_at,
            created_at=self.created_at,
        )

    @staticmethod
    def from_entity(customer: Customer) -> "CustomerModel":
        """Converts the domain entity to the persistence model."""
        # Extracts the string value from the Email VO
        email_str = (
            customer.email.value
            if isinstance(customer.email, Email)
            else customer.email
        )

        model = CustomerModel(
            id=customer.id, name=customer.name, email=email_str
        )

        if customer.created_at is not None:
            model.created_at = customer.created_at
        if customer.updated_at is not None:
            model.updated_at = customer.updated_at

        return model

    def __repr__(self) -> str:
        """Returns a string representation of the model."""
        return f"<CustomerModel(id={self.id}, email='{self.email}')>"
