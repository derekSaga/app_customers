from __future__ import annotations

from src.domain.services.customer_service import CustomerRegistrationService
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


class CreateCustomer:
    """
    Caso de Uso: Criar Cliente.
    Orquestra o Chain of Responsibility.
    """

    def __init__(
        self,
        cache: ICustomerControlCache,
        publisher: ICustomerMessagePublisher,
        service: CustomerRegistrationService,
        uow: IDBCustomerRepository,
    ):
        # Montagem da Chain
        # Redis -> Domain (Service) -> Publish
        self.cache = cache
        self.publisher = publisher
        self.service = service
        self.uow = uow

    async def execute(self, dto: CustomerCreate) -> CustomerRead:
        async with self.cache, self.uow:
            redis_handler = RedisCheckHandler(self.cache)
            domain_handler = DomainValidationHandler(service=self.service)
            publisher_handler = PublishHandler(self.publisher)

            redis_handler.set_next(domain_handler).set_next(publisher_handler)

            context = CustomerRegistrationContext(dto=dto)

            customer = await redis_handler.handle(context)

            return CustomerRead.from_entity(customer)
