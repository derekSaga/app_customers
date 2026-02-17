from collections.abc import Callable
from typing import Any

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
    def __init__(
        self,
        uow_factory: Callable[[], IDBCustomerRepository],
        usecase_factory: Callable[
            [IDBCustomerRepository], CustomerCreateUseCase
        ],
    ):
        self.uow_factory = uow_factory
        self.usecase_factory = usecase_factory

    def extract_input(
        self, message: Message[dict[Any, Any]], context: dict[str, Any]
    ) -> Customer:
        payload = message.data
        return Customer(
            id=payload["id"],
            name=payload["name"],
            email=Email(str(payload["email"]["value"])),
        )

    async def handle_message(
        self, message: Message[dict[Any, Any]], context: dict[str, Any]
    ) -> None:
        """Sobrescreve o método base para
        gerenciar o ciclo de vida da sessão."""
        input_data = self.extract_input(message, context)
        async with self.uow_factory() as uow: 
            use_case = self.usecase_factory(uow) 
            await use_case.execute(input_data)
