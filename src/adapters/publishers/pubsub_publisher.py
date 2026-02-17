import asyncio
import uuid
from concurrent.futures import Future
from typing import Any

from asgi_correlation_id import correlation_id
from google.cloud.pubsub_v1 import PublisherClient
from loguru import logger

from src.adapters.publishers.base_publisher import BasePublisher
from src.config.settings import settings


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

    def _get_correlation_id(self) -> str:
        """Sobrescreve para pegar do contexto ASGI."""
        return correlation_id.get() or str(uuid.uuid4())

    async def send_message(
        self,
        destination: str,
        body: str,
        attributes: dict[str, str]
    ) -> None:
        """
        Envia a mensagem para o tópico do Pub/Sub e aguarda a confirmação.
        """
        topic_path = self.pubsub_client.topic_path(
            self.project_id, destination
        )

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def callback(pubsub_future: Future[str]) -> None:
            try:
                result = pubsub_future.result()
                loop.call_soon_threadsafe(future.set_result, result)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)

        # Publica a mensagem no Pub/Sub
        publish_future = self.pubsub_client.publish(
            topic_path, body.encode("utf-8"), **attributes
        )
        publish_future.add_done_callback(callback)

        try:
            msg_id = await future
            logger.info(f"Published message ID: {msg_id}")
        except Exception as e:
            logger.error(f"A message failed to publish: {e}", exc_info=True)
            raise e
