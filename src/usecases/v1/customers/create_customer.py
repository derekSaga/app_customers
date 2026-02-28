"""
This module defines the use cases for creating a customer.

`InitiateCustomerCreation` orchestrates the Chain of Responsibility for
initiating customer creation, which includes checking Redis, validating the
domain, and publishing a message.

`CustomerCreateUseCase` is responsible for persisting the customer to the
database.
"""
from __future__ import annotations

from loguru import logger

from src.domain.entities.customer import Customer
from src.domain.services.customer_service import CustomerRegistrationService
from src.usecases.ports.usecase_interface import IUsecase
from src.usecases.v1.customers.handlers.domain_validation_handler import (
    DomainValidationHandler,
)
from src.usecases.v1.customers.handlers.publish_handler import PublishHandler
from src.usecases.v1.customers.handlers.redis_check_handler import (
    RedisCheckHandler,
)
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerControlCache,
    ICustomerMessagePublisher,
    IDBCustomerRepository,
)
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class InitiateCustomerCreation(IUsecase[CustomerCreate, CustomerRead]):
    """
    Use Case: Initiate Customer Creation.

    Orchestrates the Chain of Responsibility.
    """

    def __init__(
        self,
        cache: ICustomerControlCache,
        publisher: ICustomerMessagePublisher,
        service: CustomerRegistrationService,
        repository: IDBCustomerRepository,
    ):
        """
        Initializes the use case with its dependencies.

        Args:
            cache: The cache for customer control.
            publisher: The message publisher.
            service: The customer registration service.
            repository: The database repository.
        """
        # Chain setup
        # Redis -> Domain (Service) -> Publish
        self.cache = cache
        self.publisher = publisher
        self.service = service
        self.repository = repository

    async def execute(self, input_data: CustomerCreate) -> CustomerRead:
        """
        Executes the use case.

        Args:
            input_data: The customer creation data.

        Returns:
            The created customer data.
        """
        logger.info(
            f"Initiating customer creation flow for email: {input_data.email}"
        )

        redis_handler = RedisCheckHandler(self.cache)
        domain_handler = DomainValidationHandler(service=self.service)
        publisher_handler = PublishHandler(self.publisher)

        redis_handler.set_next(domain_handler).set_next(publisher_handler)

        context = CustomerRegistrationContext(dto=input_data)

        customer = await redis_handler.handle(context)

        logger.info(
            f"Customer creation initiated successfully. ID: {customer.id}"
        )

        return CustomerRead.from_entity(customer)


class CustomerCreateUseCase(IUsecase[Customer, CustomerRead]):
    """Use Case for creating a customer."""

    def __init__(
        self,
        repository: IDBCustomerRepository,
    ):
        """
        Initializes the use case with its dependencies.

        Args:
            repository: The database repository.
        """
        self.repository = repository

    async def execute(self, input_data: Customer) -> CustomerRead:
        """
        Executes the use case.

        Args:
            input_data: The customer data.

        Returns:
            The created customer data.
        """
        logger.info(f"Persisting customer {input_data.id} to database.")
        created_customer = await self.repository.add(input_data)
        logger.info(f"Customer {created_customer.id} persisted successfully.")
        return CustomerRead.from_entity(created_customer)
