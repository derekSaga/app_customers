from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.domain.entities.customer import Customer


class CustomerCreate(BaseModel):
    """Input: Dados necessários para criar um cliente."""

    name: str
    email: EmailStr
    # Phone removido para alinhar com sua Entity atual


class CustomerRead(BaseModel):
    """Output: Dados retornados para quem chamou."""

    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(customer: Customer) -> "CustomerRead":
        return CustomerRead(
            id=customer.id,
            name=customer.name,
            email=str(customer.email),
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
