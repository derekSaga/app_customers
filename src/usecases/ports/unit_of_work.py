from abc import ABC, abstractmethod
from types import TracebackType


class IUnitOfWork(ABC):
    """
    Porta para Transações Atômicas:
    Garante que tudo seja salvo junto ou nada seja salvo.
    """

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "IUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
