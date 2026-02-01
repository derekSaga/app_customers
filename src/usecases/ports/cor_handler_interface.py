# --- Chain of Responsibility Handlers ---

from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class IHandler[T](ABC):
    """Classe base para os handlers da corrente."""

    def __init__(self, next_handler: "IHandler[T] | None" = None):
        self._next_handler = next_handler

    def set_next(self, handler: "IHandler[T]") -> "IHandler[T]":
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, context: T) -> Any:
        if self._next_handler:
            return await self._next_handler.handle(context)
        return None
