from collections.abc import AsyncGenerator

from thatsoundbot.db.redis import RedisClient


async def get_redis() -> AsyncGenerator[RedisClient, None]:
    """
    Redis client dependency for use in handlers.
    
    This function is used internally by RedisMiddleware.
    For use in handlers, simply add `redis: RedisClient` parameter.
    
    Example:
        @router.message(Command("test"))
        async def test_handler(message: Message, redis: RedisClient) -> None:
            has_spotify = await redis.has_spotify_integration(hgramid)
    """
    redis_client = RedisClient()
    async with redis_client:
        yield redis_client
