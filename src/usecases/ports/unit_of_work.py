from types import TracebackType
from typing import Protocol


class IUnitOfWork(Protocol):
    """
    Porta para Transações Atômicas:
    Garante que tudo seja salvo junto ou nada seja salvo.
    """

    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def __enter__(self) -> "IUnitOfWork": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
