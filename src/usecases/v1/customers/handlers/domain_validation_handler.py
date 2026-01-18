from typing import Any

from src.domain.services.customer_service import CustomerRegistrationService
from src.domain.value_objects.email import Email
from src.usecases.ports.cor_handler_interface import Handler
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class DomainValidationHandler(Handler[CustomerRegistrationContext]):
    """2. Verifica no Banco (Source of Truth) e Cria Entidade via Service."""

    def __init__(
        self,
        service: CustomerRegistrationService,
        next_handler: Handler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.service = service

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        email_vo = Email(context.dto.email)

        # O Service verifica no banco e cria a entidade
        customer = self.service.register_new_customer(
            context.dto.name, email_vo
        )

        # Passa a entidade criada para o próximo passo
        context.customer = customer
        return await super().handle(context)
