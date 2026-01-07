from loguru import logger

from thatsoundbot.models.tsapi import RecentTracksView, TrackView
from thatsoundbot.settings import get_tsapi_settings
from thatsoundbot.utils.http_client import HttpClient


async def get_recent_tracks(hgramid: str) -> list[TrackView | None]:
    logger.info("[{hgramid}] [sound] request tracks", hgramid=hgramid[:8])

    tsapi_settings = get_tsapi_settings()
    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL +  f"/{hgramid}/recent",
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [sound] unknow api error: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        return []

    tracks_dict = response.json()
    if not tracks_dict.get("tracks"):
        return []

    recent = RecentTracksView.model_validate(tracks_dict)
    return recent.tracks
