"""
Adapter for publishing customer-related messages.

This module provides an adapter that bridges the domain-specific message
publishing interface (`ICustomerMessagePublisher`) with a concrete
infrastructure implementation (`PubSubPublisher`).
"""
from src.adapters.publishers.pubsub_publisher import PubSubPublisher
from src.config.settings import settings
from src.domain.entities.customer import Customer
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerMessagePublisher,
)


class CustomerMessageAdapter(PubSubPublisher, ICustomerMessagePublisher):
    """
    A concrete adapter for publishing customer creation events.

    This class inherits from `PubSubPublisher` to handle the low-level
    details of publishing to a Pub/Sub topic and implements the
    `ICustomerMessagePublisher` interface, which is defined by the
    application's domain logic.
    """

    DESTINATION = settings.CUSTOMER_CREATE_TOPIC
    EVENT_TYPE = "com.derekcompany.customer.create"

    async def publish_customer_creation(self, customer: Customer) -> None:
        """
        Publishes a message indicating that a customer has been created.

        This method uses the underlying `publish_message` method from the
        `PubSubPublisher` to send a structured event to the configured
        destination topic.

        Args:
            customer: The `Customer` entity that has been created.
        """
        await self.publish_message(
            destination=self.DESTINATION,
            payload=customer,
            event_type=self.EVENT_TYPE,
        )
