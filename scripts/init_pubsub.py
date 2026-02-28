"""
This script initializes Pub/Sub topics and subscriptions 
based on the project's settings.

It creates main topics, their corresponding subscriptions, 
and also sets up Dead
Letter Queues (DLQs) for each topic to handle message delivery failures.
This setup is crucial for ensuring that messages 
are not lost and can be debugged
if they fail to be processed after multiple retries.
"""
import os

from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1
from loguru import logger

# Try to import settings, fallback to environment variables or defaults
try:
    from src.config.settings import settings

    PROJECT_ID = settings.PUBSUB_PROJECT_ID

    # Define the list of topics here based on settings or direct strings
    TOPICS_CONFIG = [
        {
            "topic": settings.CUSTOMER_CREATE_TOPIC,
            "subscription": settings.CUSTOMER_CREATE_TOPIC_SUBSCRIPTION,
        },
        # Add new topics here:
        # {"topic": "order-created", "subscription": "order-created-sub"},
    ]
except ImportError:
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-gcp-project")
    TOPICS_CONFIG = [
        {"topic": "customer-created", "subscription": "customer-created-sub"}
    ]


def create_topic(
    publisher: pubsub_v1.PublisherClient, topic_path: str
) -> None:
    """Creates a topic if it doesn't exist."""
    try:
        publisher.create_topic(request={"name": topic_path})
        logger.info(f"Topic created: {topic_path}")
    except AlreadyExists:
        logger.warning(f"Topic already exists: {topic_path}")


def create_subscription(
    subscriber: pubsub_v1.SubscriberClient,
    subscription_path: str,
    topic_path: str,
    dead_letter_policy: dict[str, str] | None = None,
) -> None:
    """Creates a subscription if it doesn't exist."""
    try:
        request = {
            "name": subscription_path,
            "topic": topic_path,
            "ack_deadline_seconds": 60,
        }

        if dead_letter_policy:
            request["dead_letter_policy"] = dead_letter_policy

        subscriber.create_subscription(request=request)
        logger.info(f"Subscription created: {subscription_path}")
    except AlreadyExists:
        logger.warning(f"Subscription already exists: {subscription_path}")

        # Optional: Update DLQ policy if subscription already exists
        if dead_letter_policy:
            update_request = {
                "subscription": {
                    "name": subscription_path,
                    "dead_letter_policy": dead_letter_policy,
                },
                "update_mask": {"paths": ["dead_letter_policy"]},
            }
            try:
                subscriber.update_subscription(request=update_request)
                logger.info(
                    "Subscription updated with "
                    f"DLQ policy: {subscription_path}"
                )
            except Exception as e:
                logger.error(f"Error updating existing subscription: {e}")


def setup_topic_resources(
    publisher: pubsub_v1.PublisherClient,
    subscriber: pubsub_v1.SubscriberClient,
    config: dict[str, str],
) -> None:
    """Configures Topic, Subscription and DLQ for a configuration entry."""
    topic_name = config["topic"]
    sub_name = config["subscription"]

    # DLQ names
    dlq_topic_name = f"{topic_name}-dlq"
    dlq_sub_name = f"{sub_name}-dlq"

    # Full paths
    main_topic_path = publisher.topic_path(PROJECT_ID, topic_name)
    main_sub_path = subscriber.subscription_path(PROJECT_ID, sub_name)

    dlq_topic_path = publisher.topic_path(PROJECT_ID, dlq_topic_name)
    dlq_sub_path = subscriber.subscription_path(PROJECT_ID, dlq_sub_name)

    # 1. Create DLQ Topic
    create_topic(publisher, dlq_topic_path)

    # 2. Create DLQ Subscription
    # DLQs usually don't have another DLQ, so no policy here.
    create_subscription(subscriber, dlq_sub_path, dlq_topic_path)

    # 3. Create Main Topic
    create_topic(publisher, main_topic_path)

    # 4. Create Main Subscription pointing to the DLQ
    # Configure to send to DLQ after 5 failed attempts
    dlq_policy = {
        "dead_letter_topic": dlq_topic_path,
        "max_delivery_attempts": 5,
    }

    create_subscription(
        subscriber,
        main_sub_path,
        main_topic_path,
        dead_letter_policy=dlq_policy,
    )


def init_pubsub() -> None:
    """Orchestrates the creation of Pub/Sub resources."""
    logger.info(f"Starting Pub/Sub configuration in project: {PROJECT_ID}")

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    for config in TOPICS_CONFIG:
        setup_topic_resources(publisher, subscriber, config)

    logger.success("Pub/Sub configuration complete!")


if __name__ == "__main__":
    # Ensures that environment variables are loaded if necessary
    init_pubsub()
