from loguru import logger

from thatsoundbot.core.models.tsapi import RecentTracksView, IntegrationsTracks
from thatsoundbot.settings import get_tsapi_settings
from thatsoundbot.utils.http_client import HttpClient


async def get_recent_tracks(hgramid: str) -> IntegrationsTracks:
    logger.info("[{hgramid}] [sound] request tracks", hgramid=hgramid[:8])

    empty_result = IntegrationsTracks.model_construct(spotify=[], yandex_music=[])
    tsapi_settings = get_tsapi_settings()
    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL +  f"/{hgramid}/recent",
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [sound] unknow api error: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        return empty_result

    tracks_dict = response.json()
    if not tracks_dict.get("tracks"):
        return empty_result

    recent = RecentTracksView.model_validate(tracks_dict)
    return recent.tracks
