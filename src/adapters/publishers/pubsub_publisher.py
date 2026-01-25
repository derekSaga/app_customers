import uuid
from concurrent.futures import Future
from typing import Any

from asgi_correlation_id import correlation_id
from google.cloud.pubsub_v1 import PublisherClient
from loguru import logger

from src.config.settings import settings
from src.domain.entities.message import MessageHeader
from src.usecases.ports.base_publisher import BasePublisher


class PubSubPublisher(BasePublisher[Any]):
    """
    Implementação do Publisher utilizando Google Cloud Pub/Sub.
    """

    def __init__(
        self,
        pubsub_client: PublisherClient,
        project_id: str = settings.PUBSUB_PROJECT_ID,
    ) -> None:
        self.pubsub_client = pubsub_client
        self.project_id = project_id

    def __callback(self, publish_future: Future[str]) -> None:
        try:
            logger.info(f"Published message ID: {publish_future.result()}")
        except Exception as e:
            logger.error(f"A message failed to publish: {e}", exc_info=True)
            raise e

    def build_header(self) -> MessageHeader:
        return MessageHeader(
            correlation_id=correlation_id.get() or str(uuid.uuid4())
        )

    async def send_message(self, destination: str, body: str) -> None:
        """
        Envia a mensagem para o tópico do Pub/Sub de forma não bloqueante.
        """
        topic_path = self.pubsub_client.topic_path(
            self.project_id, destination
        )
        # Publica a mensagem no Pub/Sub
        publish_future = self.pubsub_client.publish(
            topic_path, body.encode("utf-8")
        )
        publish_future.add_done_callback(self.__callback)
