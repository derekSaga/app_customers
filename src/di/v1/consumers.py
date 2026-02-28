"""
Dependency Injection for Message Consumers.

This module provides factory functions to create and configure all message
consumers and their dependencies, such as the Pub/Sub client and the
consumer manager.
"""
import asyncio
import functools

from google.cloud.pubsub_v1 import SubscriberClient

from src.adapters.consumers.consumer_manager import ConsumerManager
from src.adapters.consumers.handlers.create_customer_handler import (
    CreateCustomerHandler,
)
from src.adapters.consumers.pubsub_consumers.pubsub_consumer import (
    PubSubConsumer,
)
from src.config.settings import settings
from src.di.v1.get_create_customer_uc import (
    get_create_customer_uc,
    get_customer_uow_factory,
)


@functools.lru_cache
def get_subscriber_client() -> SubscriberClient:
    """
    Returns a singleton instance of the Pub/Sub SubscriberClient.

    This function is cached to ensure that the same client instance is
    reused across the application, which is useful for sharing gRPC
    connections between multiple consumers.

    Returns:
        A singleton `SubscriberClient` instance.
    """
    return SubscriberClient()


async def get_consumer_manager() -> ConsumerManager:
    """
    Factory to create and assemble all message consumers for the application.

    This function should be called during application startup to ensure that
    the correct event loop is captured and used by the consumers. It
    instantiates each consumer with its specific handler and dependencies.

    Returns:
        A `ConsumerManager` instance containing all configured consumers.
    """
    client = get_subscriber_client()

    # Ensure we use the currently running event loop (e.g., from Uvicorn)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()

    # Consumer 1: Handles customer creation messages
    create_customer_consumer = PubSubConsumer(
        subscription_id=settings.CUSTOMER_CREATE_TOPIC_SUBSCRIPTION,
        handler=CreateCustomerHandler(
            uow_factory=get_customer_uow_factory,
            usecase_factory=get_create_customer_uc,
        ),
        project_id=settings.PUBSUB_PROJECT_ID,
        client=client,
        loop=loop,
    )

    return ConsumerManager(consumers=[create_customer_consumer])
