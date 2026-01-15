import asyncio
from uuid import UUID

from aiogram import Bot
from aiogram.types import FSInputFile, ChosenInlineResult
from loguru import logger

from thatsoundbot.core.models.tsapi import TrackView, ScrobbleStatus
from thatsoundbot.db.redis import RedisService
from thatsoundbot.services.telegram import backup_track, create_telegram_filename, create_caption, attach_audio_in_message
from thatsoundbot.services.tsapi import patch_file_id, scrobble_track
from thatsoundbot.settings import get_settings, get_tsripper_settings



async def fetch_file_path_periodically(redis: RedisService, scrobble_id: UUID) -> str | None:
    settings = get_settings()

    for attempt in range(1, settings.FETCH_FILE_ATTEMPTS + 1):
        await asyncio.sleep(settings.FETCH_FILE_SLEEP_TIME)
        if path := await redis.get_track_path(scrobble_id=scrobble_id):
            return path

    logger.error("[scrobble] [{scrobble_id}] failed to fetch after attempts", scrobble_id=scrobble_id)
    return None



async def get_files_paths(redis: RedisService, scrobble_id: UUID) -> tuple[str, str] | None:
    file_path = await fetch_file_path_periodically(redis=redis, scrobble_id=scrobble_id)
    if not file_path:
        return None

    thumbnail_path = await redis.get_track_thumbnail_path(scrobble_id=scrobble_id)
    if not thumbnail_path:
        logger.error("[scrobble] Failed to get path thumbnail: {scrobble_id}", scrobble_id=scrobble_id.hex[:8])
        return None

    return file_path, thumbnail_path


async def process_backup_track(redis: RedisService, bot: Bot, hgramid: str, scrobble_id: UUID, track: TrackView) -> str | None:
    result = await get_files_paths(redis=redis, scrobble_id=scrobble_id)
    if not result:
        return None
    file_path, thumbnail_path = result

    new_file_id = await backup_track(
        bot=bot,
        audio=FSInputFile(path=file_path, filename=create_telegram_filename(track=track)),
        thumbnail=FSInputFile(path=thumbnail_path, filename="thumbnail.jpg"),
        caption=create_caption(track=track)
    )
    if not new_file_id:
        return None

    await patch_file_id(hgramid=hgramid, track_id=track.id, new_file_id=new_file_id)
    logger.success("[{hgramid}] [scrobble] [caching] success", hgramid=hgramid[:8])
    return new_file_id



async def process_chosen_result(redis: RedisService, bot: Bot, chosen_result: ChosenInlineResult, hgramid: str) -> None:
    tsripper_settings = get_tsripper_settings()
    file_id = None

    selected_track = await redis.get_result_query(result_id=chosen_result.result_id)
    if not selected_track:
        logger.error(
            "[{hgramid}] [scrobble] chosen result ({result_id}) doesn't exists",
            hgramid=hgramid[:8],
            result_id=chosen_result.result_id
        )
        return

    if not tsripper_settings.IN_USE:
        await bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text=selected_track.url,
        )
        return


    scrobble_result = await scrobble_track(hgramid=hgramid, selected_track=selected_track)
    if not scrobble_result:
        return

    match scrobble_result.status:
        case ScrobbleStatus.CACHED:
            logger.info("[{hgramid}] [scrobble] using cached track", hgramid=hgramid[:8])
            file_id = scrobble_result.file_id
        case ScrobbleStatus.CREATED:
            logger.info("[{hgramid}] [scrobble] caching new track", hgramid=hgramid[:8])
            if scrobble_result.scrobble_id is None:
                logger.error("[{hgramid}] [scrobble] scrobble_id is None for CREATED status", hgramid=hgramid[:8])
                return
            file_id = await process_backup_track(
                redis=redis,
                bot=bot,
                hgramid=hgramid,
                scrobble_id=scrobble_result.scrobble_id,
                track=selected_track,
            )
        case _:
            logger.warning("[{hgramid}] [scrobble] invalid scrobble status: {scrobble_status}", hgramid=hgramid[:8], scrobble_status=scrobble_result.status)

    if file_id and chosen_result.inline_message_id:
        await attach_audio_in_message(
            bot=bot,
            hgramid=hgramid,
            inline_message_id=chosen_result.inline_message_id,
            file_id=file_id
        )
