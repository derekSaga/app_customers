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
) -> IDBCustomerRepository:
    return SQLAlchemyCustomerRepository(session=session)


def get_message_publisher() -> CustomerMessageAdapter:
    return CustomerMessageAdapter(pubsub_client=get_pubsub_client())


# --- 3. Domain Services Factories ---


def get_customer_registration_service(
    repository: IDBCustomerRepository,
) -> CustomerRegistrationService:
    return CustomerRegistrationService(checker=repository)


# --- 4. UseCase Factory ---


async def get_uow() -> AsyncGenerator[IDBCustomerRepository]:
    """Dependency para gerenciar o ciclo de vida do Banco de Dados na API."""
    # Cria a sessão e o repositório
    uow = get_customer_repository(async_session_factory())
    async with uow:
        yield uow


async def get_cache_uow() -> AsyncGenerator[ICustomerControlCache]:
    """Dependency para gerenciar o ciclo de vida do Cache na API."""
    cache = get_redis_cache()
    async with cache:
        yield cache


def get_initiate_customer_creation_uc(
    repository: IDBCustomerRepository = Depends(get_uow),
    cache: ICustomerControlCache = Depends(get_cache_uow),
) -> InitiateCustomerCreation:
    """
    Factory principal para o caso de uso InitiateCustomerCreation.
    Utiliza Depends para que o FastAPI gerencie o commit/rollback dos recursos.
    """
    return InitiateCustomerCreation(
        cache=cache,
        publisher=get_message_publisher(),
        service=get_customer_registration_service(repository),
        repository=repository,
    )


def get_create_customer_uc(
    uow: IDBCustomerRepository,
) -> CustomerCreateUseCase:
    """
    Alias para get_initiate_customer_creation_uc para compatibilidade.
    """
    return CustomerCreateUseCase(repository=uow)


def get_customer_uow_factory() -> IDBCustomerRepository:
    """Factory para criar o Unit of Work (Repositório)."""
    return get_customer_repository(async_session_factory())
