"""
This module defines the `DomainValidationHandler`, which is a handler in
the Chain of Responsibility for creating a customer.

This handler is responsible for validating the domain, which includes
checking for email uniqueness and creating a `Customer` entity. It uses the
`CustomerRegistrationService` to perform the validation.
"""
from datetime import datetime
from typing import Any
from uuid import uuid4

from loguru import logger

from src.domain.entities.customer import Customer
from src.domain.services.customer_service import CustomerRegistrationService
from src.domain.value_objects.email import Email
from src.usecases.ports.cor_handler_interface import IHandler
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class DomainValidationHandler(IHandler[CustomerRegistrationContext]):
    """2. Checks in the Database (Source of Truth) and Creates Entity via
    Service."""

    def __init__(
        self,
        service: CustomerRegistrationService,
        next_handler: IHandler[CustomerRegistrationContext] | None = None,
    ):
        """
        Initializes the handler with a customer registration service.

        Args:
            service: The customer registration service.
            next_handler: The next handler in the chain.
        """
        super().__init__(next_handler)
        self.service = service

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        """
        Handles the domain validation.

        Args:
            context: The customer registration context.

        Returns:
            The result of the next handler.
        """
        email_vo = Email(context.dto.email)

        logger.info(f"Validating email availability in DB: {email_vo}")
        # The Service checks in the database (Source of Truth)
        await self.service.validate_email_availability(email_vo)

        # Creates the entity
        now = datetime.now()
        customer_id = uuid4()
        customer = Customer(
            id=customer_id,
            name=context.dto.name,
            email=email_vo,
            created_at=now,
            updated_at=now,
        )

        logger.info(
            f"Domain validation passed. Generated Customer ID: {customer.id}"
        )

        # Passes the created entity to the next step
        context.customer = customer
        return await super().handle(context)
