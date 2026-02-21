from abc import ABC, abstractmethod
from typing import Any


class IConsumerHandler[TMessage](ABC):
    """Interface para handlers de mensagens (Consumers)."""

    @abstractmethod
    async def handle_message(
        self, message: TMessage, context: dict[str, Any]
    ) -> None:
        """
        Processa a mensagem recebida.

        Args:
            message: A mensagem decodificada
                (ex: Envelope, JSON dict, ou bytes).
            context: Metadados do contexto de execução (ex: tracing, headers).
        """
        ...


class BaseUseCaseHandler[TMessage, TInput, TOutput](
    IConsumerHandler[TMessage], ABC
):
    """
    Classe base para handlers que executam um Caso de Uso (IUsecase).
    Responsável por adaptar a mensagem recebida para o input do Use Case.
    """

    @abstractmethod
    def extract_input(
        self, message: TMessage, context: dict[str, Any]
    ) -> TInput:
        """Converte a mensagem e contexto no DTO de entrada do Use Case."""
        ...

    @abstractmethod
    async def handle_message(
        self, message: TMessage, context: dict[str, Any]
    ) -> None:
        """Processa a mensagem, geralmente gerenciando o Unit of Work."""
        ...
