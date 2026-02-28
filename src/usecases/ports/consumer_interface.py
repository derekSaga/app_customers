"""
This module defines the `IConsumer` interface, which is an abstract base
class for message consumers.

This interface defines the contract that all message consumers must follow,
ensuring that they can be started and can process messages in a consistent
way.
"""
from abc import ABC, abstractmethod
from typing import Any


class IConsumer(ABC):
    """
    Abstract base class for message consumers.

    It defines the contract that all message consumers must follow.
    """

    @abstractmethod
    async def _callback(self, message: bytes, context: dict[str, Any]) -> None:
        """
        Abstract method to process incoming messages.

        Args:
            message: The message payload.
            context: The message context.
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Abstract method to start listening for messages."""
        pass
