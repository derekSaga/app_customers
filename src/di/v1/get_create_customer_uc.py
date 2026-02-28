"""
This module provides dependency injection (DI) factories for creating and
assembling all the components required for the customer creation use cases.

It follows a layered approach, defining:
1.  Providers for infrastructure clients (Redis, Pub/Sub).
2.  Factories for adapters (repositories, caches, publishers).
3.  Factories for domain services.
4.  Factories for the use cases themselves.

It leverages `functools.lru_cache` to create singleton clients and FastAPI's
`Depends` for managing the lifecycle of resources like database sessions and
cache connections.
"""
import functools
from collections.abc import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from google.cloud.pubsub_v1 import PublisherClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache.redis_cache import RedisCache
from src.adapters.database.repositories.customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.adapters.database.session import async_session_factory
from src.adapters.publishers.customer_message_adapter import (
    CustomerMessageAdapter,
)
from src.config.settings import settings
from src.domain.services.customer_service import CustomerRegistrationService
from src.usecases.v1.customers.create_customer import (
    CustomerCreateUseCase,
    InitiateCustomerCreation,
)
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerControlCache,
    IDBCustomerRepository,
)

# --- 1. Infrastructure Providers (Singletons) ---


@functools.lru_cache
def get_redis_client() -> redis.Redis:
    """Returns a singleton instance of the Redis client."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    )


@functools.lru_cache
async def get_pubsub_client() -> PublisherClient:
    """Returns a singleton instance of the PubSub client."""
    return PublisherClient()


# --- 2. Adapters Factories ---


class CustomerRedisCache(RedisCache, ICustomerControlCache):
    """Customer-specific Redis cache."""

    pass


def get_redis_cache() -> CustomerRedisCache:
    """Returns a customer-specific Redis cache."""
    return CustomerRedisCache(client=get_redis_client())


def get_customer_repository(
    session: AsyncSession,
) -> IDBCustomerRepository:
    """
    Returns a customer repository.

    Args:
        session: The database session.

    Returns:
        A customer repository.
    """
    return SQLAlchemyCustomerRepository(session=session)


async def get_message_publisher() -> CustomerMessageAdapter:
    """Returns a message publisher."""
    pubsub_client = await get_pubsub_client()
    return CustomerMessageAdapter(pubsub_client=pubsub_client)


# --- 3. Domain Services Factories ---


def get_customer_registration_service(
    repository: IDBCustomerRepository,
) -> CustomerRegistrationService:
    """
    Returns a customer registration service.

    Args:
        repository: The customer repository.

    Returns:
        A customer registration service.
    """
    return CustomerRegistrationService(checker=repository)


# --- 4. UseCase Factory ---


async def get_uow() -> AsyncGenerator[IDBCustomerRepository]:
    """Dependency to manage the database lifecycle in the API."""
    # Creates the session and the repository
    uow = get_customer_repository(async_session_factory())
    async with uow:
        yield uow


async def get_cache_uow() -> AsyncGenerator[ICustomerControlCache]:
    """Dependency to manage the cache lifecycle in the API."""
    cache = get_redis_cache()
    async with cache:
        yield cache


async def get_initiate_customer_creation_uc(
    repository: IDBCustomerRepository = Depends(get_uow),
    cache: ICustomerControlCache = Depends(get_cache_uow),
) -> InitiateCustomerCreation:
    """
    Main factory for the InitiateCustomerCreation use case.

    Uses `Depends` so that FastAPI manages the commit/rollback of resources.

    Args:
        repository: The customer repository.
        cache: The customer control cache.

    Returns:
        An instance of the InitiateCustomerCreation use case.
    """
    publisher = await get_message_publisher()
    return InitiateCustomerCreation(
        cache=cache,
        publisher=publisher,
        service=get_customer_registration_service(repository),
        repository=repository,
    )


def get_create_customer_uc(
    uow: IDBCustomerRepository,
) -> CustomerCreateUseCase:
    """
    Alias for get_initiate_customer_creation_uc for compatibility.

    Args:
        uow: The unit of work.

    Returns:
        An instance of the CustomerCreateUseCase.
    """
    return CustomerCreateUseCase(repository=uow)


def get_customer_uow_factory() -> IDBCustomerRepository:
    """Factory to create the Unit of Work (Repository)."""
    return get_customer_repository(async_session_factory())
