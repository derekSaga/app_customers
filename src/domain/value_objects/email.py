import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Value Object para representar um email válido e imutável."""

    value: str

    def __post_init__(self) -> None:
        """Valida no construtor — falha rápido se inválido."""
        if not self._is_valid(self.value):
            raise ValueError(f"Email inválido: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        # Regex simples para validação de email
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def __str__(self) -> str:
        return self.value
