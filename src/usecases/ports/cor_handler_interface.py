# --- Chain of Responsibility Handlers ---

from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class Handler[T](ABC):
    """Classe base para os handlers da corrente."""

    def __init__(self, next_handler: "Handler[T] | None" = None):
        self._next_handler = next_handler

    @abstractmethod
    async def handle(self, context: T) -> Any:
        if self._next_handler:
            return await self._next_handler.handle(context)
        return None
