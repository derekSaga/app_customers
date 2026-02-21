from typing import Any

from loguru import logger

from src.domain.entities.customer import Customer
from src.usecases.ports.cor_handler_interface import IHandler
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerMessagePublisher,
)
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class PublishHandler(IHandler[CustomerRegistrationContext]):
    """3. Publica mensagem para persistência assíncrona."""

    def __init__(
        self,
        publisher: ICustomerMessagePublisher,
        next_handler: IHandler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.publisher = publisher

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        customer = context.customer
        if not customer:
            raise ValueError("Entidade Customer não encontrada no contexto.")

        customer_data = Customer(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )

        logger.info(
            f"Publishing customer creation event for ID: {customer.id}"
        )
        await self.publisher.publish_customer_creation(customer_data)

        return customer
