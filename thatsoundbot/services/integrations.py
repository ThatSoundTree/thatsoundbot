from thatsoundbot.db import RedisClient


async def get_user_integrations(hgramid: str) -> dict:
    redis = RedisClient.current()
    has_spotify = await redis.has_spotify_integration(hgramid=hgramid)
    has_yandex_music = await redis.has_yandex_music_integration(hgramid=hgramid)
    return {"spotify": has_spotify, "YandexMusic": has_yandex_music}
