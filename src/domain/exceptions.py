"""
This module defines custom exceptions for the domain layer.

These exceptions represent business rule violations and other
domain-specific errors.
"""


class DomainError(Exception):
    """Base exception for domain errors."""

    pass


class CustomerAlreadyExistsError(DomainError):
    """Raised when trying to register a customer that already exists."""

    def __init__(self, email: str):
        super().__init__(f"Customer with email '{email}' already exists.")
