from src.domain.services.customer_service import CustomerRegistrationService
from src.domain.value_objects.email import Email
from src.usecases.v1.customers.ports.repositories import ICustomerRepository
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead


class CreateCustomer:
    """
    Caso de Uso: Criar Cliente.
    Orquestra o serviço de domínio e a persistência.
    """

    def __init__(
        self, repository: ICustomerRepository, service: CustomerRegistrationService
    ):
        self.repository = repository
        self.service = service

    def execute(self, dto: CustomerCreate) -> CustomerRead:
        with self.repository:
            # 1. Converter DTO -> Value Object
            email = Email(dto.email)

            # 2. Delegar regra de negócio para o Domain Service
            customer = self.service.register_new_customer(dto.name, email)

            # 3. Persistência
            self.repository.add(customer)
            self.repository.commit()

            # 4. Retorno
            return CustomerRead.from_entity(customer)
