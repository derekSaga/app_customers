import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Message[T]:
    """
    Estrutura compatível com CloudEvents v1.0 (Structured Content Mode).
    """

    data: T
    type: str
    source: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    specversion: str = "1.0"
    time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    datacontenttype: str = "application/json"
    correlation_id: str | None = None
