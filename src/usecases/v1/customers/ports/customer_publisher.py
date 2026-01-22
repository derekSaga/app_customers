from src.adapters.publishers.pubsub_publisher import PubSubPublisher
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

    async def publish_customer_creation(self, customer: Customer) -> None:
        """
        Implementação do contrato definido pelo Use Case.
        """
        destination = "events.customer.created"

        await self.publish(destination=destination, payload=customer)
