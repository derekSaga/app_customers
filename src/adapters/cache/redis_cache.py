from types import TracebackType

import redis.asyncio as redis
from redis.asyncio.client import Pipeline

from src.usecases.ports.repositories import ICacheRepository


class RedisCache(ICacheRepository[str, str]):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client
        self._pipeline: Pipeline | None = None

    @property
    def pipeline(self) -> Pipeline:
        if not self._pipeline:
            raise RuntimeError(
                "Transação não iniciada. Use 'async with repository' "
                "antes de realizar operações de escrita."
            )
        return self._pipeline

    async def __aenter__(self) -> "RedisCache":
        # Inicia o pipeline para agrupar comandos (transação)
        self._pipeline = self.client.pipeline()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._pipeline:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
            self._pipeline = None

    async def commit(self) -> None:
        await self.pipeline.execute()

    async def rollback(self) -> None:
        if self._pipeline:
            # Esvazia a fila de comandos do pipeline sem executar
            self._pipeline.reset()  # type: ignore[no-untyped-call]

    async def get(self, key: str) -> str | None:
        # Leitura direta (fora da transação para obter dados atuais)
        value = await self.client.get(key)
        return str(value) if value is not None else None

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key) > 0)

    async def set(
        self, key: str, value: str, expire: int | None = None
    ) -> None:
        await self.pipeline.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        await self.pipeline.delete(key)
