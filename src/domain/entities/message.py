"""
This module defines a generic `Message` class that is compatible with the
CloudEvents v1.0 specification (Structured Content Mode).

This class serves as a standardized envelope for all messages within the
system, ensuring interoperability and consistent metadata.
"""
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Message[T]:
    """
    A generic message class compatible with the CloudEvents v1.0
    specification (Structured Content Mode).

    This class serves as a standardized envelope for all messages within the
    system, ensuring interoperability and consistent metadata.

    Attributes:
        data: The payload of the message.
        type: The type of event.
        source: The source of the event.
        id: A unique identifier for the event.
        specversion: The version of the CloudEvents specification.
        time: The time the event was generated.
        datacontenttype: The content type of the `data` attribute.
        correlation_id: An optional identifier for tracking related events.
    """

    data: T
    type: str
    source: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    specversion: str = "1.0"
    time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    datacontenttype: str = "application/json"
    correlation_id: str | None = None
