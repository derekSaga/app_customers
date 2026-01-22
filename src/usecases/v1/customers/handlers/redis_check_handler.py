from typing import Any

from src.usecases.ports.cor_handler_interface import Handler
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerControlCache,
)
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class RedisCheckHandler(Handler[CustomerRegistrationContext]):
    """1. Verifica e cadastra no Redis (Short-circuit)."""

    def __init__(
        self,
        cache: ICustomerControlCache,
        next_handler: Handler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.cache = cache

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        email = context.dto.email

        # Verifica se já existe no cache
        if await self.cache.exists(email):
            raise ValueError("Cliente já existe (Cache).")

        # Cadastra no Redis (Lock temporário)
        await self.cache.set(email, "processing", expire=60)

        return await super().handle(context)
