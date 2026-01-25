import functools

import redis.asyncio as redis
from google.cloud.pubsub_v1 import PublisherClient

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
from src.usecases.v1.customers.create_customer import CreateCustomer

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


def get_redis_cache() -> RedisCache:
    return RedisCache(client=get_redis_client())


def get_customer_repository() -> SQLAlchemyCustomerRepository:
    return SQLAlchemyCustomerRepository(session_factory=async_session_factory)


def get_message_publisher() -> CustomerMessageAdapter:
    return CustomerMessageAdapter(pubsub_client=get_pubsub_client())


# --- 3. Domain Services Factories ---


def get_customer_registration_service() -> CustomerRegistrationService:
    return CustomerRegistrationService(checker=get_customer_repository())


# --- 4. UseCase Factory ---


def get_create_customer_use_case() -> CreateCustomer:
    """
    Factory principal para o caso de uso CreateCustomer.
    Injeta todas as dependências necessárias.
    """
    return CreateCustomer(
        cache=get_redis_cache(),
        publisher=get_message_publisher(),
        service=get_customer_registration_service(),
    )
