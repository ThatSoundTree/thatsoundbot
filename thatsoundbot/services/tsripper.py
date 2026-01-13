import asyncio
from uuid import UUID

from aiogram.types import FSInputFile
from loguru import logger

from thatsoundbot.core.models.tsapi import TrackView
from thatsoundbot.db import RedisClient
from thatsoundbot.services.telegram import backup_track, create_telegram_filename, create_caption
from thatsoundbot.settings import get_tsapi_settings,  get_settings
from thatsoundbot.utils.http_client import HttpClient


async def scrobble_track(hgramid: str, selected_track: TrackView) -> None | str | UUID:
    tsapi_settings = get_tsapi_settings()
    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble",
        params={"track_id": selected_track.id, "track_provider": selected_track.provider},
        headers=tsapi_settings.get_header()
    )

    if response.status_code == 200:
        resp = response.json()
        return resp["tfile_url"]
    elif response.status_code != 503:
        logger.error(
            "[{hgramid}] [scrobble] [{track_id}] unexpected api error: {error_text}",
            hgramid=hgramid,
            track_id=selected_track.id,
            error_text=response.text[:200],
        )
        return None

    resp = response.json()
    return UUID(resp["id"])


async def fetch_file_path_periodically(scrobble_id: UUID) -> str | None:
    settings = get_settings()
    redis = RedisClient.current()
    attempt = 0
    track_path = None
    while attempt < settings.FETCH_FILE_ATTEMPTS:
        await asyncio.sleep(settings.FETCH_FILE_SLEEP_TIME)
        track_path = await redis.get_track_path(scrobble_id=scrobble_id)
        if not track_path:
            attempt += 1
            continue
        break

    if not track_path:
        logger.error("[scrobble] [{scrobble_id}] failed to fetch after attempts", scrobble_id=scrobble_id)
        return None

    return track_path


async def process_backup_track(hgramid: str, scrobble_id: UUID, track: TrackView) -> str:
    tsapi_settings = get_tsapi_settings()
    redis = RedisClient.current()

    file_path = await fetch_file_path_periodically(scrobble_id=scrobble_id)
    if not file_path:
        raise RuntimeError

    thumbnail_path = await redis.get_track_thumbnail_path(scrobble_id=scrobble_id)

    if not thumbnail_path:
        raise RuntimeError

    new_file_id = await backup_track(
        audio=FSInputFile(path=file_path, filename=create_telegram_filename(track=track)),
        thumbnail=FSInputFile(path=thumbnail_path, filename="thumbnail.jpg"),
        caption=create_caption(track=track)
    )


    response = await HttpClient.patch(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble/",
        params={"external_track_id": track.id, "tfile_url": new_file_id},
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error(
            "[{hgramid}] [scrobble] [caching] unexpected api error: {error_text}",
            hgramid=hgramid[:8],
            error_text=response.text[:200]
        )
        return new_file_id

    logger.success("[{hgramid}] [scrobble] [caching] success", hgramid=hgramid[:8])
    return new_file_id
