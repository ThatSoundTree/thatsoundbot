import asyncio

from aiogram import Bot
from loguru import logger

from thatsoundbot.core.models import SpotifyTrack
from thatsoundbot.services.task_status_checker import check_task_status_periodically
from thatsoundbot.settings import get_settings
from thatsoundbot.utils.http_client2 import TSDirectHTTPClient


async def create_download_task(
    track: SpotifyTrack,
    htelegram_id: str,
    message_id: str | None,
    bot: Bot | None = None,
    chat_id: int | None = None,
    is_inline: bool = False,
) -> dict:
    """Create download task for track on external backend."""
    settings = get_settings()
    backend_url = f"{settings.DIRECT_API_URL}/api/v1/tasks"

    json_data = {
        "track": {
            "id": track.id,
            "name": track.name,
            "artists": track.artists,
            "album": track.album,
            "album_cover_url": track.album_cover_url,
            "download_url": track.external_urls,
            "duration_ms": track.duration_ms,
        },
        "htelegram_id": htelegram_id,
        "message_id": message_id,
    }

    logger.info(
        "Sending download task request to TSDirect: track_id={track_id}, htelegram_id={htelegram_id}, message_id={message_id}, url={url}",
        track_id=track.id,
        htelegram_id=htelegram_id[:8],
        message_id=message_id,
        url=backend_url,
    )
    response = await TSDirectHTTPClient.post(backend_url, json=json_data)
    response.raise_for_status()
    result = response.json() if response.content else {}
    logger.info("Download task created successfully: track_id={track_id}", track_id=track.id)

    task_id = result.get("task_id")
    if task_id and bot and message_id:
        check_interval = settings.TASK_STATUS_CHECK_INTERVAL
        asyncio.create_task(
            check_task_status_periodically(
                task_id, htelegram_id, check_interval, bot, chat_id, message_id, is_inline, track.id
            )
        )
    else:
        logger.warning("No task_id in response, skipping status checker: result={result}", result=result)

    return result
