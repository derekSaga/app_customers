from datetime import datetime
from typing import Protocol
from uuid import uuid4

from src.domain.entities.customer import Customer
from src.domain.value_objects.email import Email


class ICustomerExistenceCheck(Protocol):
    """Interface funcional necessária para o serviço verificar duplicidade."""

    def exists_by_email(self, email: str) -> bool: ...


class CustomerRegistrationService:
    """
    Domain Service: Responsável pelas regras de negócio da criação de cliente.
    Garante que não existam duplicatas antes de instanciar a entidade.
    """

    def __init__(self, checker: ICustomerExistenceCheck):
        self.checker = checker

    def register_new_customer(self, name: str, email: Email) -> Customer:
        # 1. Regra de Negócio: Unicidade de E-mail
        if self.checker.exists_by_email(str(email)):
            raise ValueError("Cliente já existe com este e-mail.")

        # 2. Criação da Entidade
        now = datetime.now()
        return Customer(
            id=uuid4(),
            name=name,
            email=email,
            created_at=now,
            updated_at=now,
        )
