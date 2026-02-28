"""
This module defines the `Customer` entity, which represents a customer with
a unique identity and mutable state. It also defines a
`CustomerCreateMessage` for creating customers.
"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.message import Message
from src.domain.value_objects.email import Email


@dataclass
class Customer:
    """Entity with a unique and mutable identity."""

    id: UUID
    name: str
    email: Email
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def change_email(self, new_email_str: str) -> None:
        """Changes email — creates a new Value Object with validation."""
        new_email = Email(new_email_str)
        self.email = new_email
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Equality by ID (not by value)."""
        if not isinstance(other, Customer):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Returns the hash of the ID."""
        return hash(self.id)


class CustomerCreateMessage(Message[Customer]):
    """Message for creating a customer."""

    pass
