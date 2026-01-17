from abc import ABC, abstractmethod
from types import TracebackType


class IUnitOfWork(ABC):
    """
    Porta para Transações Atômicas:
    Garante que tudo seja salvo junto ou nada seja salvo.
    """

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    def __enter__(self) -> "IUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            self.rollback()
