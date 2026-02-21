import asyncio
import json
from typing import Any, TypeVar

from asgi_correlation_id import correlation_id
from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.pubsub_v1.subscriber.message import Message as PubSubMessage
from loguru import logger

from src.config.settings import settings
from src.domain.entities.message import Message
from src.usecases.ports.consumer_handler_interface import IConsumerHandler
from src.usecases.ports.consumer_interface import IConsumer

T = TypeVar("T")


class PubSubConsumer(IConsumer):
    """
    Implementação concreta de IConsumer usando Google Pub/Sub.
    Utiliza um handler injetado para processar a mensagem (Strategy Pattern).
    """

    def __init__(
        self,
        subscription_id: str,
        handler: IConsumerHandler[Message[T]],
        client: SubscriberClient,
        project_id: str = settings.PUBSUB_PROJECT_ID,
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.handler = handler
        self.client = client
        self.subscription_path = self.client.subscription_path(
            self.project_id, self.subscription_id
        )
        self._loop = loop or asyncio.get_event_loop()

    def __repr__(self) -> str:
        return f"PubSubConsumer(subscription={self.subscription_id})"

    def start(self) -> None:
        """Inicia o consumo de mensagens em background."""
        logger.info(f"Starting PubSub consumer for: {self.subscription_path}")
        try:
            self.client.subscribe(
                self.subscription_path, callback=self.__internal_callback
            )
        except Exception as e:
            logger.error(
                f"Failed to subscribe to {self.subscription_path}: {e}"
            )
            raise e

    def __internal_callback(self, message: PubSubMessage) -> None:
        """
        Callback síncrono chamado pela lib do Pub/Sub.
        Faz a ponte para o loop assíncrono.
        """
        context: dict[Any, Any] = {}
        try:
            logger.info(
                f"Queue {self.subscription_id} "
                f"Received message: {message.message_id}"
            )
            future = asyncio.run_coroutine_threadsafe(
                self._process_message(message, context), self._loop
            )
            # Aguarda o resultado para confirmar (ack) ou rejeitar (nack)
            future.result(timeout=60)
            message.ack()
        except Exception as e:
            correlation_id.set(context.get("correlation_id", "unknown"))
            logger.error(f"Error processing message {message.message_id}: {e}")
            message.nack()

    async def _process_message(
        self, message: PubSubMessage, context: dict[Any, Any]
    ) -> None:
        """Wrapper interno para preparar chamada ao _callback."""
        context.update(dict(message.attributes))
        logger.info(
            f"Processing message {message.message_id} with context: {context}"
        )
        await self._callback(message.data, context)

    async def _callback(self, message: bytes, context: dict[str, Any]) -> None:
        """
        Deserializa a mensagem e chama o consume.
        """
        try:
            logger.info(f"Raw message data: {str(message)}")
            decoded_data = message.decode("utf-8")
            payload_dict = json.loads(decoded_data)

            msg = Message(
                data=payload_dict.get(
                    "data", payload_dict.get("payload", payload_dict)
                ),
                type=payload_dict.get("type", None),
                source=payload_dict.get(
                    "source", context.get("source", "pubsub.subscriber")
                ),
                correlation_id=(
                    context.get("correlation_id")
                    or payload_dict.get("correlation_id")
                ),
            )
            correlation_id.set(msg.correlation_id)
            await self.handler.handle_message(msg, context)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise e
