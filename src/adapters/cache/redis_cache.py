"""
This module provides an implementation of the ICacheRepository using Redis.

The RedisCache class uses the redis-py async client to interact with a Redis
server. It supports transactional operations through Redis pipelines.
"""
from types import TracebackType

import redis.asyncio as redis
from redis.asyncio.client import Pipeline

from src.usecases.ports.repositories_interface import ICacheRepository


class RedisCache(ICacheRepository[str, str]):
    """
    An implementation of the ICacheRepository that uses Redis as a backend.

    This class supports atomic operations through Redis pipelines, which are
    used as transactions.
    """

    def __init__(self, client: redis.Redis) -> None:
        """
        Initializes the Redis client.

        Args:
            client: An instance of redis.Redis.
        """
        self.client = client
        self._pipeline: Pipeline | None = None

    @property
    def pipeline(self) -> Pipeline:
        """
        Returns the current pipeline, raising a RuntimeError if no
        transaction is active.
        """
        if not self._pipeline:
            raise RuntimeError(
                "Transaction not started. Use 'async with repository' "
                "before performing write operations."
            )
        return self._pipeline

    async def __aenter__(self) -> "RedisCache":
        """
        Starts a pipeline to group commands (transaction).
        """
        # Starts the pipeline to group commands (transaction)
        self._pipeline = self.client.pipeline()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Manages the transaction lifecycle, committing or rolling back on exit.
        """
        if self._pipeline:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
            self._pipeline = None

    async def commit(self) -> None:
        """
        Executes the pipeline.
        """
        await self.pipeline.execute()

    async def rollback(self) -> None:
        """
        Discards the pipeline.
        """
        if self._pipeline:
            # Clears the pipeline's command queue without executing
            await self._pipeline.reset()  # type: ignore[no-untyped-call]

    async def get(self, key: str) -> str | None:
        """
        Retrieves a value from the cache.

        Args:
            key: The key to retrieve.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        # Direct read (outside the transaction to get current data)
        value = await self.client.get(key)
        return str(value) if value is not None else None

    async def exists(self, key: str) -> bool:
        """
        Checks if a key exists in the cache.

        Args:
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return bool(await self.client.exists(key) > 0)

    async def set(
        self, key: str, value: str, expire: int | None = None
    ) -> None:
        """
        Sets a value in the cache.

        Args:
            key: The key to set.
            value: The value to set.
            expire: The expiration time in seconds.
        """
        await self.pipeline.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        """
        Deletes a key from the cache.

        Args:
            key: The key to delete.
        """
        await self.pipeline.delete(key)
