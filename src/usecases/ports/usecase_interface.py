"""
This module defines the `IUsecase` interface, which is a base interface for
use cases.

It defines the contract that all use cases must follow, ensuring that they
can be executed in a consistent way.
"""
from abc import ABC, abstractmethod


class IUsecase[TInput, TOutput](ABC):
    """Base interface for Use Cases."""

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Executes the business logic of the use case."""
        ...
