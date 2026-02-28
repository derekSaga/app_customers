"""
Health check endpoints for the service.

This module provides routers for liveness and readiness probes.
"""
import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Response, status
from google.cloud.pubsub_v1 import PublisherClient
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.adapters.database.session import engine
from src.config.settings import settings
from src.di.v1.get_create_customer_uc import (
    get_pubsub_client,
    get_redis_client,
)

router = APIRouter()


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict[str, str]:
    """
    Liveness probe: Checks if the application process is running.
    """
    return {"status": "ok"}


async def get_db_connection() -> AsyncGenerator[AsyncConnection]:
    """
    Dependency to get a database connection.
    """
    async with engine.connect() as connection:
        yield connection


async def check_postgres(db: AsyncConnection) -> str:
    """Check database connection."""
    try:
        await db.execute(text("SELECT 1"))
        return "ok"
    except Exception as e:
        return f"error: {e}"


async def check_redis(redis_client: AsyncRedis) -> str:
    """Check Redis connection."""
    try:
        await redis_client.ping()  # type: ignore
        return "ok"
    except Exception as e:
        return f"error: {e}"


def _check_pubsub_blocking(
    pubsub_client: PublisherClient, topic_path: str
) -> str:
    """Blocking check for Pub/Sub topic."""
    try:
        pubsub_client.get_topic(topic=topic_path)
        return "ok"
    except Exception as e:
        return f"error: {e}"


async def check_pubsub(pubsub_client: PublisherClient) -> str:
    """Check Pub/Sub topic existence via a thread pool."""
    topic_path = pubsub_client.topic_path(
        settings.PUBSUB_PROJECT_ID, settings.CUSTOMER_CREATE_TOPIC
    )
    return await asyncio.to_thread(
        _check_pubsub_blocking, pubsub_client, topic_path
    )


@router.get("/ready")
async def readiness_probe(
    response: Response,
    db: AsyncConnection = Depends(get_db_connection),
    redis_client: AsyncRedis = Depends(get_redis_client),
    pubsub_client: PublisherClient = Depends(get_pubsub_client),
) -> dict[str, str]:
    """
    Readiness probe: Concurrently checks all external dependencies.

    Returns a detailed status of each service. If any service fails,
    the endpoint will return a 503 Service Unavailable status code.
    """
    results = await asyncio.gather(
        check_postgres(db),
        check_redis(redis_client),
        check_pubsub(pubsub_client),
    )

    service_statuses = {
        "postgres": results[0],
        "redis": results[1],
        "pubsub": results[2],
    }

    if any(status != "ok" for status in service_statuses.values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return service_statuses
