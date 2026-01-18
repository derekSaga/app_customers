from typing import Any

from src.usecases.ports.cor_handler_interface import Handler
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerMessagePublisher,
)


class PublishHandler(Handler[CustomerRegistrationContext]):
    """3. Publica mensagem para persistência assíncrona."""

    def __init__(
        self,
        publisher: ICustomerMessagePublisher,
        next_handler: Handler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.publisher = publisher

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        customer = context.customer
        if not customer:
            raise ValueError("Entidade Customer não encontrada no contexto.")

        payload = {
            "id": str(customer.id),
            "name": customer.name,
            "email": str(customer.email),
            "created_at": customer.created_at.isoformat(),
        }
        await self.publisher.publish_customer_creation(payload)

        return customer
