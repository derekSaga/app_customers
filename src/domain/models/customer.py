from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.customer import Customer
from src.domain.models.base import Base
from src.domain.value_objects.email import Email


class CustomerModel(Base):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    def to_entity(self) -> Customer:
        """Converte o modelo de persistência para a entidade de domínio."""
        # Assumindo que o construtor do Customer aceita id, name e o VO Email
        return Customer(
            id=self.id,
            name=self.name,
            email=Email(self.email),
            updated_at=self.updated_at,
            created_at=self.created_at,
        )

    @staticmethod
    def from_entity(customer: Customer) -> "CustomerModel":
        """Converte a entidade de domínio para o modelo de persistência."""
        # Extrai o valor string do VO Email
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
        return f"<CustomerModel(id={self.id}, email='{self.email}')>"
