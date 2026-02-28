"""
This module defines the `CustomerRegistrationService`, a domain service
responsible for the business logic of customer creation.

It ensures that no duplicates exist before instantiating the entity. It also
defines the `ICustomerUniquenessChecker` protocol, which defines the
contract for checking customer uniqueness.
"""
from typing import Protocol

from src.domain.exceptions import CustomerAlreadyExistsError
from src.domain.value_objects.email import Email


class ICustomerUniquenessChecker(Protocol):
    """
    Interface (Port) for uniqueness checking.

    Defines the contract necessary for the Domain Service to query existence.
    """

    async def exists_by_email(self, email: str) -> bool: ...


class CustomerRegistrationService:
    """
    Domain Service: Responsible for the business rules of customer creation.

    Ensures that no duplicates exist before instantiating the entity.
    """

    def __init__(self, checker: ICustomerUniquenessChecker):
        """
        Initializes the service with a uniqueness checker.

        Args:
            checker: An object that implements the
                `ICustomerUniquenessChecker` protocol.
        """
        self.checker = checker

    async def validate_email_availability(self, email: Email) -> None:
        """
        Validates that an email is available for registration.

        Args:
            email: The email to validate.

        Raises:
            CustomerAlreadyExistsError: If a customer with the same email
                already exists.
        """
        # 1. Business Rule: Email uniqueness
        result = await self.checker.exists_by_email(str(email))
        if result:
            raise CustomerAlreadyExistsError(str(email))
