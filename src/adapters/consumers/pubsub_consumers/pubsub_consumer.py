"""
Google Pub/Sub specific implementation of a message consumer.

This module provides the `PubSubConsumer` class, which connects to a Google
Cloud Pub/Sub subscription and processes messages using an injected handler.
"""
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
    A concrete implementation of `IConsumer` using Google Cloud Pub/Sub.

    This class subscribes to a specific Pub/Sub subscription and delegates
    message processing to an injected handler, following the Strategy Pattern.
    It manages the asynchronous interaction with the Pub/Sub library.

    Attributes:
        project_id: The Google Cloud project ID.
        subscription_id: The ID of the Pub/Sub subscription.
        handler: The message handler responsible for processing messages.
        client: The Pub/Sub subscriber client.
        subscription_path: The full path to the subscription.
    """

    def __init__(
        self,
        subscription_id: str,
        handler: IConsumerHandler[Message[T]],
        client: SubscriberClient,
        project_id: str = settings.PUBSUB_PROJECT_ID,
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        """
        Initializes the PubSubConsumer.

        Args:
            subscription_id: The ID of the Pub/Sub subscription to listen to.
            handler: An object that implements `IConsumerHandler` to process
                incoming messages.
            client: An instance of `google.cloud.pubsub_v1.SubscriberClient`.
            project_id: The Google Cloud project ID. Defaults to the one in
                the global settings.
            loop: The asyncio event loop to use. If None, the current running
                loop is used.
        """
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.handler = handler
        self.client = client
        self.subscription_path = self.client.subscription_path(
            self.project_id, self.subscription_id
        )
        self._loop = loop or asyncio.get_event_loop()

    def __repr__(self) -> str:
        """Returns a string representation of the consumer."""
        return f"PubSubConsumer(subscription={self.subscription_id})"

    def start(self) -> None:
        """
        Starts the background consumption of messages from the subscription.

        This method initiates a subscription to the configured Pub/Sub topic.
        The Pub/Sub client library handles the message fetching in background
        threads.

        Raises:
            Exception: If the subscription fails for any reason.
        """
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
        Synchronous callback executed by the Pub/Sub library for each message.

        This method acts as a bridge to the asyncio world. It schedules the
        asynchronous `_process_message` coroutine to run on the event loop
        and waits for its completion to acknowledge (ack) or negatively
        acknowledge (nack) the message.

        Args:
            message: The message received from Pub/Sub.
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
            # Wait for the result to confirm (ack) or reject (nack)
            future.result(timeout=60)
            message.ack()
        except Exception as e:
            correlation_id.set(context.get("correlation_id", "unknown"))
            logger.error(f"Error processing message {message.message_id}: {e}")
            message.nack()

    async def _process_message(
        self, message: PubSubMessage, context: dict[Any, Any]
    ) -> None:
        """
        Internal wrapper to prepare the call to the main callback.

        This coroutine extracts attributes from the Pub/Sub message and adds
        them to the context before calling the final processing callback.

        Args:
            message: The message received from Pub/Sub.
            context: The context dictionary to be populated.
        """
        context.update(dict(message.attributes))
        logger.info(
            f"Processing message {message.message_id} with context: {context}"
        )
        await self._callback(message.data, context)

    async def _callback(self, message: bytes, context: dict[str, Any]) -> None:
        """
        Deserializes the message and invokes the injected handler.

        This is the core message processing logic. It decodes the message
        body, constructs a standardized `Message` object, and passes it to
        the `IConsumerHandler` for business logic execution.

        Args:
            message: The raw message body as bytes.
            context: The message context, including attributes.

        Raises:
            Exception: Propagates exceptions from the handler or from
                deserialization errors.
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
            logger.error(f"Deserialization or handler error: {e}")
            raise e
