from datetime import datetime
from typing import Any
from uuid import uuid4

from src.domain.entities.customer import Customer
from src.domain.services.customer_service import CustomerRegistrationService
from src.domain.value_objects.email import Email
from src.usecases.ports.cor_handler_interface import IHandler
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class DomainValidationHandler(IHandler[CustomerRegistrationContext]):
    """2. Verifica no Banco (Source of Truth) e Cria Entidade via Service."""

    def __init__(
        self,
        service: CustomerRegistrationService,
        next_handler: IHandler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.service = service

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        email_vo = Email(context.dto.email)

        # O Service verifica no banco (Source of Truth)
        await self.service.validate_email_availability(email_vo)

        # Cria a entidade
        now = datetime.now()
        customer = Customer(
            id=uuid4(),
            name=context.dto.name,
            email=email_vo,
            created_at=now,
            updated_at=now,
        )

        # Passa a entidade criada para o próximo passo
        context.customer = customer
        return await super().handle(context)
