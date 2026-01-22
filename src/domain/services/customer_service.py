from datetime import datetime
from typing import Protocol
from uuid import uuid4

from src.domain.entities.customer import Customer
from src.domain.value_objects.email import Email


class ICustomerUniquenessChecker(Protocol):
    """
    Interface (Porta) para verificação de unicidade.
    Define o contrato necessário para o Domain Service consultar existência.
    """

    async def exists_by_email(self, email: str) -> bool: ...


class CustomerRegistrationService:
    """
    Domain Service: Responsável pelas regras de negócio da criação de cliente.
    Garante que não existam duplicatas antes de instanciar a entidade.
    """

    def __init__(self, checker: ICustomerUniquenessChecker):
        self.checker = checker

    async def register_new_customer(self, name: str, email: Email) -> Customer:
        # 1. Regra de Negócio: Unicidade de E-mail
        result = await self.checker.exists_by_email(str(email))
        if result:
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
