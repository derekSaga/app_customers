import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class MessageHeader:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    content_type: str = "application/json"
    schema_version: str = "1.0"


@dataclass(frozen=True)
class Message[T]:
    header: MessageHeader
    payload: T
