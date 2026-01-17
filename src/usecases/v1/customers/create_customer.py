from src.domain.services.customer_service import CustomerRegistrationService
from src.domain.value_objects.email import Email
from src.usecases.v1.customers.ports.db_customer_repository import (
    IDBCustomerRepository,
)
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead


class CreateCustomer:
    """
    Caso de Uso: Criar Cliente.
    Orquestra o serviço de domínio e a persistência.
    """

    def __init__(
        self,
        repository: IDBCustomerRepository,
        service: CustomerRegistrationService,
    ):
        self.repository = repository
        self.service = service

    async def execute(self, dto: CustomerCreate) -> CustomerRead:
        async with self.repository:
            # 1. Converter DTO -> Value Object
            email = Email(dto.email)

            # 2. Delegar regra de negócio para o Domain Service
            customer = self.service.register_new_customer(dto.name, email)

            # 3. Persistência
            await self.repository.add(customer)
            await self.repository.commit()

            # 4. Retorno
            return CustomerRead.from_entity(customer)
