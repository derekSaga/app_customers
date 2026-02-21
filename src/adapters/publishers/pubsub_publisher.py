import asyncio
import uuid
from concurrent.futures import Future
from typing import Any

from asgi_correlation_id import correlation_id
from google.cloud.pubsub_v1 import PublisherClient
from loguru import logger

from src.adapters.publishers.base_publisher import BasePublisher
from src.adapters.publishers.exceptions import (
    PublishFailedError,
    PublishTimeoutError,
)
from src.config.settings import settings


class PubSubPublisher(BasePublisher[Any]):
    """
    Implementação do Publisher utilizando Google Cloud Pub/Sub.
    Gerencia a ponte entre a biblioteca síncrona do Google e o loop assíncrono.
    """

    def __init__(
        self,
        pubsub_client: PublisherClient,
        project_id: str = settings.PUBSUB_PROJECT_ID,
    ) -> None:
        self.pubsub_client = pubsub_client
        self.project_id = project_id
        self.publish_timeout = 10.0

    def _get_correlation_id(self) -> str:
        """Sobrescreve para pegar do contexto ASGI."""
        return correlation_id.get() or str(uuid.uuid4())

    async def send_message(
        self, destination: str, body: str, attributes: dict[str, str]
    ) -> None:
        """
        Envia a mensagem para o tópico do Pub/Sub e aguarda a confirmação.
        """
        # Verifica se o destination já é um caminho completo ou apenas o ID
        if "/" in destination:
            topic_path = destination
        else:
            topic_path = self.pubsub_client.topic_path(
                self.project_id, destination
            )

        loop = asyncio.get_running_loop()
        aio_future = loop.create_future()

        def callback(pubsub_future: Future[str]) -> None:
            try:
                result = pubsub_future.result()
                loop.call_soon_threadsafe(aio_future.set_result, result)
            except Exception as e:
                loop.call_soon_threadsafe(aio_future.set_exception, e)

        # Publica a mensagem no Pub/Sub
        publish_future = self.pubsub_client.publish(
            topic_path, body.encode("utf-8"), **attributes
        )
        publish_future.add_done_callback(callback)

        try:
            msg_id = await asyncio.wait_for(
                aio_future, timeout=self.publish_timeout
            )
            logger.info(f"Published message ID: {msg_id} to {destination}")
        except TimeoutError:
            error_msg = (
                f"Timeout publishing to {destination} "
                f"after {self.publish_timeout}s"
            )
            logger.error(error_msg)
            raise PublishTimeoutError(error_msg) from None
        except Exception as e:
            error_msg = f"A message failed to publish to {destination}: {e}"
            logger.error(error_msg, exc_info=True)
            raise PublishFailedError(error_msg) from e
