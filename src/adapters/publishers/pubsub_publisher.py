"""
This module provides a concrete implementation of the `BasePublisher` for
Google Cloud Pub/Sub.

It manages the bridge between the synchronous Google library and the
asynchronous event loop.
"""
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
    Publisher implementation using Google Cloud Pub/Sub.

    Manages the bridge between the synchronous Google library and the
    asynchronous event loop.
    """

    def __init__(
        self,
        pubsub_client: PublisherClient,
        project_id: str = settings.PUBSUB_PROJECT_ID,
    ) -> None:
        """
        Initializes the publisher with a Pub/Sub client and project ID.

        Args:
            pubsub_client: The Pub/Sub client.
            project_id: The Google Cloud project ID.
        """
        self.pubsub_client = pubsub_client
        self.project_id = project_id
        self.publish_timeout = 10.0

    def _get_correlation_id(self) -> str:
        """
        Overrides to get the correlation ID from the ASGI context.

        Returns:
            The correlation ID.
        """
        return correlation_id.get() or str(uuid.uuid4())

    async def send_message(
        self, destination: str, body: str, attributes: dict[str, str]
    ) -> None:
        """
        Sends the message to the Pub/Sub topic and waits for confirmation.

        Args:
            destination: The destination topic.
            body: The message body.
            attributes: The message attributes.
        """
        # Checks if the destination is a full path or just the ID
        if "/" in destination:
            topic_path = destination
        else:
            topic_path = self.pubsub_client.topic_path(
                self.project_id, destination
            )

        loop = asyncio.get_running_loop()
        aio_future = loop.create_future()

        def callback(pubsub_future: Future[str]) -> None:
            """
            Callback to bridge the Pub/Sub future with the asyncio future.

            Args:
                pubsub_future: The future from the Pub/Sub library.
            """
            try:
                result = pubsub_future.result()
                loop.call_soon_threadsafe(aio_future.set_result, result)
            except Exception as e:
                loop.call_soon_threadsafe(aio_future.set_exception, e)

        # Publishes the message to Pub/Sub
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
