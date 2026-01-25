import functools

import redis.asyncio as redis
from fastapi import Depends
from google.cloud.pubsub_v1 import PublisherClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache.redis_cache import RedisCache
from src.adapters.database.repositories.customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.adapters.database.session import get_session
from src.adapters.publishers.customer_message_adapter import (
    CustomerMessageAdapter,
)
from src.config.settings import settings
from src.domain.services.customer_service import CustomerRegistrationService
from src.usecases.v1.customers.create_customer import CreateCustomer
from src.usecases.v1.customers.ports.customer_repositories import (
    ICustomerControlCache,
)

# --- 1. Infrastructure Providers (Singletons) ---


@functools.lru_cache
def get_redis_client() -> redis.Redis:
    """Retorna uma instância singleton do cliente Redis."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    )


@functools.lru_cache
def get_pubsub_client() -> PublisherClient:
    """Retorna uma instância singleton do cliente PubSub."""
    return PublisherClient()


# --- 2. Adapters Factories ---


class CustomerRedisCache(RedisCache, ICustomerControlCache):
    pass


def get_redis_cache() -> CustomerRedisCache:
    return CustomerRedisCache(client=get_redis_client())


def get_customer_repository(
    session: AsyncSession,
) -> SQLAlchemyCustomerRepository:
    return SQLAlchemyCustomerRepository(session=session)


def get_message_publisher() -> CustomerMessageAdapter:
    return CustomerMessageAdapter(pubsub_client=get_pubsub_client())


# --- 3. Domain Services Factories ---


def get_customer_registration_service(
    session: AsyncSession,
) -> CustomerRegistrationService:
    return CustomerRegistrationService(
        checker=get_customer_repository(session)
    )


# --- 4. UseCase Factory ---


def get_create_customer_use_case(
    session: AsyncSession = Depends(get_session),
) -> CreateCustomer:
    """
    Factory principal para o caso de uso CreateCustomer.
    Injeta todas as dependências necessárias.
    """
    repository = get_customer_repository(session)

    return CreateCustomer(
        cache=get_redis_cache(),
        publisher=get_message_publisher(),
        service=get_customer_registration_service(session),
        uow=repository,
    )
