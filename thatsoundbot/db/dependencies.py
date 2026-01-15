from thatsoundbot.db.redis import RedisClient, RedisService


async def get_redis() -> RedisService:
    client = RedisClient.client()
    return RedisService(client)
