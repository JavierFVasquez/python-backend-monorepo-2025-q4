import redis.asyncio as redis

from services.products.domain.ports import CachePort


class RedisCache(CachePort):
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            # Upstash Redis requires SSL
            self._redis = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                ssl_cert_reqs=None,  # Disable SSL certificate verification for Upstash
                socket_keepalive=True,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return self._redis

    async def get(self, key: str) -> str | None:
        client = await self._get_redis()
        return await client.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        client = await self._get_redis()
        await client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        client = await self._get_redis()
        await client.delete(key)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()

