"""
Message handler for creating a customer.

This module defines the `CreateCustomerHandler`, which is responsible for
processing messages related to customer creation, adapting them, and
executing the corresponding use case.
"""
from collections.abc import Callable
from typing import Any

from loguru import logger

from src.domain.entities.customer import Customer
from src.domain.entities.message import Message
from src.domain.value_objects.email import Email
from src.usecases.ports.consumer_handler_interface import BaseUseCaseHandler
from src.usecases.v1.customers.create_customer import CustomerCreateUseCase
from src.usecases.v1.customers.ports.customer_repositories import (
    IDBCustomerRepository,
)
from src.usecases.v1.schemas.api.customer import CustomerRead


class CreateCustomerHandler(
    BaseUseCaseHandler[Message[dict[Any, Any]], Customer, CustomerRead]
):
    """
    Handles messages for creating a new customer.

    This handler extracts customer data from a message, transforms it into a
    `Customer` domain entity, and then executes the `CustomerCreateUseCase`
    within a managed unit of work.
    """

    def __init__(
        self,
        uow_factory: Callable[[], IDBCustomerRepository],
        usecase_factory: Callable[
            [IDBCustomerRepository], CustomerCreateUseCase
        ],
    ):
        """
        Initializes the CreateCustomerHandler.

        Args:
            uow_factory: A callable that returns a Unit of Work instance,
                providing access to the customer repository.
            usecase_factory: A callable that takes a repository and returns
                an instance of the `CustomerCreateUseCase`.
        """
        self.uow_factory = uow_factory
        self.usecase_factory = usecase_factory

    def extract_input(
        self, message: Message[dict[Any, Any]], context: dict[str, Any]
    ) -> Customer:
        """
        Extracts and transforms the message payload into a Customer entity.

        Args:
            message: The incoming message containing the customer data.
            context: A dictionary with message context (not used here).

        Returns:
            A `Customer` domain entity populated with data from the message.
        """
        payload = message.data
        return Customer(
            id=payload["id"],
            name=payload["name"],
            email=Email(str(payload["email"]["value"])),
        )

    async def handle_message(
        self, message: Message[dict[Any, Any]], context: dict[str, Any]
    ) -> None:
        """
        Processes the customer creation message.

        This method orchestrates the customer creation by:
        1. Extracting the `Customer` entity from the message.
        2. Creating a Unit of Work to manage the database transaction.
        3. Instantiating the use case with the repository from the UoW.
        4. Executing the use case to persist the customer.

        Args:
            message: The message to be processed.
            context: A dictionary with message context.
        """
        logger.info(f"Worker received message. ID: {message.id}")

        input_data = self.extract_input(message, context)

        async with self.uow_factory() as uow:
            use_case = self.usecase_factory(uow)
            await use_case.execute(input_data)
