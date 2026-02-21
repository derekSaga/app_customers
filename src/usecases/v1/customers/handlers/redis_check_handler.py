from typing import Any

from loguru import logger

from src.domain.exceptions import CustomerAlreadyExistsError
from src.usecases.ports.cor_handler_interface import IHandler
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerControlCache,
)
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)


class RedisCheckHandler(IHandler[CustomerRegistrationContext]):
    """1. Verifica e cadastra no Redis (Short-circuit)."""

    def __init__(
        self,
        cache: ICustomerControlCache,
        next_handler: IHandler[CustomerRegistrationContext] | None = None,
    ):
        super().__init__(next_handler)
        self.cache = cache

    async def handle(self, context: CustomerRegistrationContext) -> Any:
        email = context.dto.email

        logger.info(f"Checking cache for email: {email}")

        # Verifica se já existe no cache
        if await self.cache.exists(email):
            logger.warning(
                f"Email {email} already exists in cache (Short-circuit)."
            )
            raise CustomerAlreadyExistsError(email)

        # Cadastra no Redis (Lock temporário)
        logger.info(f"Acquiring lock for email: {email}")
        await self.cache.set(email, "processing", expire=60)
        return await super().handle(context)
