
from loguru import logger

from thatsoundbot.db.redis import RedisService
from thatsoundbot.settings import get_tsapi_settings
from thatsoundbot.utils.http_client import HttpClient


async def create_remote_user(hgramid: str) -> None:
    tsapi_settings = get_tsapi_settings()

    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/integrations",
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [sound] failed to get integrations: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        return


async def get_user_integrations(redis: RedisService, hgramid: str) -> dict:
    has_spotify = await redis.has_spotify_integration(hgramid=hgramid)
    has_yandex_music = await redis.has_yandex_music_integration(hgramid=hgramid)
    return {"spotify": has_spotify, "YandexMusic": has_yandex_music}
