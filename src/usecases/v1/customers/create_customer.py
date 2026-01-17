from datetime import datetime
from uuid import uuid4

from src.domain.entities.customer import Customer
from src.domain.value_objects.email import Email
from src.usecases.ports.repositories import IRepository
from src.usecases.ports.unit_of_work import IUnitOfWork
from src.usecases.v1.schemas.customer import CustomerCreate, CustomerRead


class CreateCustomer:
    """
    Caso de Uso: Criar Cliente.
    Orquestra a criação da entidade e instrui a persistência via Porta.
    """

    def __init__(self, uow: IUnitOfWork, repository: IRepository[Customer, Customer]):
        # Injeção de Dependência: O UseCase pede um contrato (Interface),
        # não uma implementação concreta (SQLAlchemy).
        self.uow = uow
        self.repository = repository

    def execute(self, dto: CustomerCreate) -> CustomerRead:
        with self.uow:
            # 1. Regras de Domínio (Value Objects e Entidade)
            email = Email(dto.email)

            now = datetime.now()
            customer = Customer(
                id=uuid4(), name=dto.name, email=email, created_at=now, updated_at=now
            )

            # 2. Persistência (através da Porta)
            self.repository.add(customer)
            self.uow.commit()

            # 3. Retorno
            return CustomerRead.from_entity(customer)
