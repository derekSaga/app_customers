from abc import ABC, abstractmethod


class IUsecase[TInput, TOutput](ABC):
    """Interface base para Casos de Uso (Use Cases)."""

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Executa a lógica de negócio do caso de uso."""
        ...
