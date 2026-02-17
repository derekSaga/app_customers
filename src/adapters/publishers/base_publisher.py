import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from src.domain.entities.message import Message

T = TypeVar("T")


class BasePublisher[T](ABC):
    """
    Classe base abstrata para publicação de mensagens.
    Padroniza o formato da mensagem (Envelope) e a serialização.
    """

    def _get_correlation_id(self) -> str:
        """Hook para obter correlation_id (pode ser sobrescrito)."""
        return str(uuid.uuid4())

    @abstractmethod
    async def send_message(
        self, destination: str, body: str, attributes: dict[str, str]
    ) -> None:
        """
        Método abstrato que deve ser implementado pelo
        adapter concreto (ex: RabbitMQ, Kafka).
        Responsável pelo transporte da mensagem serializada.

        Args:
            destination: O destino da mensagem (fila, tópico, routing key).
            body: O conteúdo da mensagem já serializado em JSON.
            attributes: Metadados de transporte (headers).
        """
        ...

    async def publish(
        self,
        destination: str,
        payload: T,
        event_type: str,
        correlation_id: str | None = None,
    ) -> None:
        """
        Constrói o envelope da mensagem e a publica no destino especificado.

        Args:
            destination: O destino da mensagem.
            payload: O conteúdo da mensagem (dados do domínio).
            event_type: O tipo do evento (ex: com.empresa.customer.created).
            correlation_id: ID de correlação opcional para rastreamento.
        """
        cid = correlation_id or self._get_correlation_id()

        # 1. Construir o CloudEvent
        message = Message(
            data=payload,
            type=event_type,
            source="/v1/app-customers",
            correlation_id=cid,
        )

        # 2. Preparar atributos de transporte (Protocol Binding)
        attributes = {
            "correlation_id": cid,
            "ce-type": event_type,
            "ce-source": message.source,
            "ce-id": message.id,
        }

        # 3. Serializar para JSON (Structured Mode)
        body = json.dumps(asdict(message), default=self._json_serializer)

        # 4. Enviar com atributos
        await self.send_message(destination, body, attributes)

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Helper para serializar tipos comuns não
        suportados nativamente pelo json.dumps."""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, (UUID,)):
            return str(obj)
        return str(obj)
