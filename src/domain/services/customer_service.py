from typing import Protocol

from src.domain.exceptions import CustomerAlreadyExistsError
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

    async def validate_email_availability(self, email: Email) -> None:
        # 1. Regra de Negócio: Unicidade de E-mail
        result = await self.checker.exists_by_email(str(email))
        if result:
            raise CustomerAlreadyExistsError(str(email))
