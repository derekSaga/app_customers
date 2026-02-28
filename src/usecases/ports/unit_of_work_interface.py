"""
This module defines the `IUnitOfWork` interface, which is a port for
atomic transactions.

It ensures that all operations within a unit of work are either saved
together or not saved at all. The interface defines methods for committing
and rolling back transactions, as well as for entering and exiting a
context manager.
"""
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TypeVar

T = TypeVar("T", bound="IUnitOfWork")


class IUnitOfWork(ABC):
    """
    Port for Atomic Transactions:
    Ensures that everything is saved together or nothing is saved.
    """

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    async def __aenter__(self: T) -> T:
        """
        Enters a context manager.

        Returns:
            The unit of work instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exits a context manager, rolling back the transaction if an
        exception occurred.

        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The traceback.
        """
        if exc_type:
            await self.rollback()
