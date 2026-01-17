from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CustomerBase(BaseModel):
    """Output: Dados retornados para quem chamou."""

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
