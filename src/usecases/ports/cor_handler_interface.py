"""
This module defines the interfaces for the Chain of Responsibility (CoR)
handlers.

It includes a base interface `IHandler` that defines the contract for all
handlers in the chain. Each handler can process a request and pass it to the
next handler in the chain.
"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class IHandler[T](ABC):
    """Base class for the handlers in the chain."""

    def __init__(self, next_handler: "IHandler[T] | None" = None):
        """
        Initializes the handler with an optional next handler.

        Args:
            next_handler: The next handler in the chain.
        """
        self._next_handler = next_handler

    def set_next(self, handler: "IHandler[T]") -> "IHandler[T]":
        """
        Sets the next handler in the chain.

        Args:
            handler: The next handler.

        Returns:
            The next handler.
        """
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, context: T) -> Any:
        """
        Handles a request.

        If a next handler is set, it calls the next handler.

        Args:
            context: The request context.

        Returns:
            The result of the handler.
        """
        if self._next_handler:
            return await self._next_handler.handle(context)
        return None
