class DomainError(Exception):
    """Exceção base para erros de domínio."""

    pass


class CustomerAlreadyExistsError(DomainError):
    """Lançado quando tenta-se registrar um cliente que já existe."""

    def __init__(self, email: str):
        super().__init__(f"Cliente com email '{email}' já existe.")
