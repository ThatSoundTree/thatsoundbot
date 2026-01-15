from uuid import UUID

from loguru import logger

from thatsoundbot.core.models.tsapi import TrackView, ScrobbleResult, ScrobbleStatus
from thatsoundbot.settings import get_tsapi_settings
from thatsoundbot.utils.http_client import HttpClient


async def scrobble_track(hgramid: str, selected_track: TrackView) -> ScrobbleResult | None:
    tsapi_settings = get_tsapi_settings()

    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble",
        params={
            "track_id": selected_track.id,
            "track_provider": selected_track.provider
        },
        headers=tsapi_settings.get_header()
    )

    if response.status_code == 200:
        data = response.json()
        return ScrobbleResult(
            status=ScrobbleStatus.CACHED,
            file_id=data["tfile_url"],
        )

    if response.status_code == 503:
        data = response.json()
        return ScrobbleResult(
            status=ScrobbleStatus.CREATED,
            scrobble_id=UUID(data["id"]),
        )

    logger.error(
        "[{hgramid}] [scrobble] [{track_id}] unexpected api error: {error}",
        hgramid=hgramid,
        track_id=selected_track.id,
        error=response.text[:200],
    )

    return None


async def patch_file_id(hgramid: str, track_id: str, new_file_id: str):
    tsapi_settings = get_tsapi_settings()

    response = await HttpClient.patch(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble/",
        params={"external_track_id": track_id, "tfile_url": new_file_id},
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error(
            "[{hgramid}] [scrobble] [caching] unexpected api error: {error_text}",
            hgramid=hgramid[:8],
            error_text=response.text[:200]
        )

    logger.success("[{hgramid}] [{track_id}] success patched filed_id")
