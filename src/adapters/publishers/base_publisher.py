"""
This module defines the abstract base class for message publishers.

It standardizes the message format (Envelope) and serialization.
"""
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from src.domain.entities.message import Message

T = TypeVar("T")


class BasePublisher[T](ABC):
    """
    Abstract base class for publishing messages.

    Standardizes the message format (Envelope) and serialization.
    """

    def _get_correlation_id(self) -> str:
        """
        Hook to get the correlation_id (can be overridden).

        Returns:
            A new correlation ID.
        """
        return str(uuid.uuid4())

    @abstractmethod
    async def send_message(
        self, destination: str, body: str, attributes: dict[str, str]
    ) -> None:
        """
        Abstract method that must be implemented by the concrete adapter.

        Responsible for transporting the serialized message.

        Args:
            destination: The message destination (queue, topic, routing key).
            body: The message content already serialized in JSON.
            attributes: Transport metadata (headers).
        """
        ...

    async def publish_message(
        self,
        destination: str,
        payload: T,
        event_type: str,
        correlation_id: str | None = None,
    ) -> None:
        """
        Builds the message envelope and publishes it to the specified
        destination.

        Args:
            destination: The message destination.
            payload: The message content (domain data).
            event_type: The event type (e.g., com.company.customer.created).
            correlation_id: Optional correlation ID for tracking.
        """
        cid = correlation_id or self._get_correlation_id()

        # 1. Build the CloudEvent
        message = Message(
            data=payload,
            type=event_type,
            source="/v1/app-customers",
            correlation_id=cid,
        )

        # 2. Prepare transport attributes (Protocol Binding)
        attributes = {
            "correlation_id": cid,
            "ce-type": event_type,
            "ce-source": message.source,
            "ce-id": message.id,
        }

        # 3. Serialize to JSON (Structured Mode)
        body = json.dumps(asdict(message), default=self._json_serializer)

        # 4. Send with attributes
        await self.send_message(destination, body, attributes)

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """
        Helper for serializing common types not natively supported by
        json.dumps.

        Args:
            obj: The object to serialize.

        Returns:
            A serializable representation of the object.
        """
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, (UUID,)):
            return str(obj)
        return str(obj)
