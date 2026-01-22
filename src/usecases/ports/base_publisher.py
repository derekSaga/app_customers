import json
from abc import ABC, abstractmethod
from dataclasses import asdict, replace
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from src.domain.entities.message import Message, MessageHeader

T = TypeVar("T")


class BasePublisher[T](ABC):
    """
    Classe base abstrata para publicação de mensagens.
    Padroniza o formato da mensagem (Envelope) e a serialização.
    """

    @abstractmethod
    def build_header(
        self,
    ) -> MessageHeader: ...

    @abstractmethod
    async def send_message(self, destination: str, body: str) -> None:
        """
        Método abstrato que deve ser implementado pelo
        adapter concreto (ex: RabbitMQ, Kafka).
        Responsável pelo transporte da mensagem serializada.

        Args:
            destination: O destino da mensagem (fila, tópico, routing key).
            body: O conteúdo da mensagem já serializado em JSON.
        """
        ...

    async def publish(
        self, destination: str, payload: T, correlation_id: str | None = None
    ) -> None:
        """
        Constrói o envelope da mensagem e a publica no destino especificado.

        Args:
            destination: O destino da mensagem.
            payload: O conteúdo da mensagem (dados do domínio).
            correlation_id: ID de correlação opcional para rastreamento.
        """
        # 1. Construir o Header
        header = self.build_header()
        if correlation_id:
            header = replace(header, correlation_id=correlation_id)

        # 2. Construir o Envelope (Message)
        message = Message(header=header, payload=payload)

        # 3. Serializar para JSON
        body = json.dumps(asdict(message), default=self._json_serializer)

        # 4. Enviar
        await self.send_message(destination, body)

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Helper para serializar tipos comuns não
        suportados nativamente pelo json.dumps."""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, (UUID,)):
            return str(obj)
        return str(obj)
