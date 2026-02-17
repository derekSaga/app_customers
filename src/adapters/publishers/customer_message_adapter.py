from src.adapters.publishers.pubsub_publisher import PubSubPublisher
from src.config.settings import settings
from src.domain.entities.customer import Customer
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerMessagePublisher,
)


class CustomerMessageAdapter(PubSubPublisher, ICustomerMessagePublisher):
    """
    Adapter concreto.
    Herda de PubSubPublisher (Infraestrutura) e implementa
    ICustomerMessagePublisher (Domínio).
    """

    DESTINATION = settings.CUSTOMER_CREATE_TOPIC
    EVENT_TYPE = "com.derekcompany.customer.create"

    async def publish_customer_creation(self, customer: Customer) -> None:
        await self.publish(
            destination=self.DESTINATION,
            payload=customer,
            event_type=self.EVENT_TYPE,
        )
