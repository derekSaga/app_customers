from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.email import Email


@dataclass
class Customer:
    """Entity com identidade única e mutável."""

    id: UUID
    name: str
    email: Email
    created_at: datetime
    updated_at: datetime

    def change_email(self, new_email_str: str) -> None:
        """Altera email — cria novo Value Object com validação."""
        new_email = Email(new_email_str)
        self.email = new_email
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Igualdade por ID (não por valor)."""
        if not isinstance(other, Customer):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
