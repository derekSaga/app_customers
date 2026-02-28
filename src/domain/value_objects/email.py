"""
This module defines the `Email` value object, which represents a valid and
immutable email address.

It validates the email format upon instantiation to ensure that only valid
emails can be created.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Value Object to represent a valid and immutable email."""

    value: str

    def __post_init__(self) -> None:
        """Validates in the constructor — fails fast if invalid."""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        """
        Checks if an email is valid.

        Args:
            email: The email to validate.

        Returns:
            True if the email is valid, False otherwise.
        """
        # Simple regex for email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def __str__(self) -> str:
        """Returns the string representation of the email."""
        return self.value
