from abc import ABC, abstractmethod
from typing import Any


class IConsumer(ABC):
    @abstractmethod
    async def _callback(self, message: bytes, context: dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
