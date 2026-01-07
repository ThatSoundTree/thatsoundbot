from loguru import logger

from thatsoundbot.settings import get_tsapi_settings
from thatsoundbot.utils.http_client import HttpClient


async def get_user_integrations(hgramid: str) -> dict:
    tsapi_settings = get_tsapi_settings()

    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/integrations",
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [sound] failed to get integrations: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        return {}

    return response.json()
