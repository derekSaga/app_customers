"""
This module defines the interfaces for message handlers (consumers).

It includes a base interface `IConsumerHandler` and a more specific
`BaseUseCaseHandler` for handlers that execute a use case. These
interfaces define the contract for processing incoming messages and
adapting them to the input of a use case.
"""
from abc import ABC, abstractmethod
from typing import Any


class IConsumerHandler[TMessage](ABC):
    """Interface for message handlers (Consumers)."""

    @abstractmethod
    async def handle_message(
        self, message: TMessage, context: dict[str, Any]
    ) -> None:
        """
        Processes the received message.

        Args:
            message: The decoded message
                (e.g., Envelope, JSON dict, or bytes).
            context: Execution context metadata (e.g., tracing, headers).
        """
        ...


class BaseUseCaseHandler[TMessage, TInput, TOutput](
    IConsumerHandler[TMessage], ABC
):
    """
    Base class for handlers that execute a Use Case (IUsecase).

    Responsible for adapting the received message to the Use Case's input.
    """

    @abstractmethod
    def extract_input(
        self, message: TMessage, context: dict[str, Any]
    ) -> TInput:
        """Converts the message and context into the Use Case's input DTO."""
        ...

    @abstractmethod
    async def handle_message(
        self, message: TMessage, context: dict[str, Any]
    ) -> None:
        """Processes the message, usually by managing the Unit of Work."""
        ...
