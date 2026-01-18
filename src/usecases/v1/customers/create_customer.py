from __future__ import annotations

from src.domain.services.customer_service import CustomerRegistrationService
from src.usecases.v1.schemas.base.customer_registration_context import (
    CustomerRegistrationContext,
)
from src.usecases.v1.customers.handlers.domain_validation_handler import (
    DomainValidationHandler,
)
from src.usecases.v1.customers.handlers.publish_handler import PublishHandler
from src.usecases.v1.customers.handlers.redis_check_handler import (
    RedisCheckHandler,
)
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerCacheRepository,
    ICustomerMessagePublisher,
)
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead


class CreateCustomer:
    """
    Caso de Uso: Criar Cliente.
    Orquestra o Chain of Responsibility.
    """

    def __init__(
        self,
        cache: ICustomerCacheRepository,
        publisher: ICustomerMessagePublisher,
        service: CustomerRegistrationService,
    ):
        # Montagem da Chain
        # Redis -> Domain (Service) -> Publish
        self.chain = RedisCheckHandler(
            cache,
            next_handler=DomainValidationHandler(
                service, next_handler=PublishHandler(publisher)
            ),
        )

    async def execute(self, dto: CustomerCreate) -> CustomerRead:
        # Contexto da requisição
        context = CustomerRegistrationContext(dto=dto)

        # Executa a corrente
        customer = await self.chain.handle(context)

        return CustomerRead.from_entity(customer)
