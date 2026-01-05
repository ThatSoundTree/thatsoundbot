from aiogram import Bot
from loguru import logger

from thatsoundbot.core.handlers.messages.audio import (
    handle_inline_audio_message,
    handle_regular_audio_message,
)
from thatsoundbot.repositories.tasks import download_task_file, wait_for_task_ready
from thatsoundbot.settings import get_settings
from thatsoundbot.utils.files import get_filename_from_task_data


async def check_task_status_periodically(
    task_id: str,
    htelegram_id: str,
    check_interval: int,
    bot: Bot,
    chat_id: int | None,
    message_id: str,
    is_inline: bool = False,
    track_id: str = "",
) -> None:
    """Periodically check task status until it's ready, then download and send file."""
    settings = get_settings()
    status_url = f"{settings.DIRECT_API_URL}/api/v1/tasks/{htelegram_id}/{task_id}"
    download_url = f"{settings.DIRECT_API_URL}/api/v1/tasks/{task_id}"
    htelegram_id_short = htelegram_id[:8]

    logger.info(
        "Starting periodic task status check: task_id={task_id}, htelegram_id={htelegram_id_short}, interval={interval}s",
        task_id=task_id,
        htelegram_id_short=htelegram_id_short,
        interval=check_interval,
    )

    task_data = await wait_for_task_ready(status_url, task_id, htelegram_id_short, check_interval)
    logger.info(
        "Task is ready for download: task_id={task_id}, htelegram_id={htelegram_id_short}",
        task_id=task_id,
        htelegram_id_short=htelegram_id_short,
    )

    filename = get_filename_from_task_data(task_data, task_id)
    file_path = await download_task_file(download_url, task_id)
    logger.info("File downloaded: task_id={task_id}, file_path={file_path}", task_id=task_id, file_path=file_path)

    if not track_id:
        track_id = task_data.get("track_id") or ""

    # Get thumbnail for audio file
    from thatsoundbot.utils.thumbnail import get_thumbnail_from_mp3, get_thumbnail_from_url

    thumbnail = await get_thumbnail_from_mp3(file_path)
    if not thumbnail:
        album_cover_url = task_data.get("album_cover_url")
        if album_cover_url:
            thumbnail = await get_thumbnail_from_url(album_cover_url)

    try:
        if is_inline:
            await handle_inline_audio_message(
                bot, file_path, filename, message_id, settings.TEMP_FILE_CHANNEL, track_id, thumbnail
            )
            logger.info(
                "File replaced in inline message, stopping status checks: task_id={task_id}, htelegram_id={htelegram_id_short}",
                task_id=task_id,
                htelegram_id_short=htelegram_id_short,
            )
        elif chat_id and message_id:
            await handle_regular_audio_message(bot, file_path, filename, chat_id, message_id, thumbnail)
            logger.info(
                "File replaced in regular message, stopping status checks: task_id={task_id}, htelegram_id={htelegram_id_short}",
                task_id=task_id,
                htelegram_id_short=htelegram_id_short,
            )
        else:
            logger.warning(
                "Cannot edit message: chat_id={chat_id}, message_id={message_id}",
                chat_id=chat_id,
                message_id=message_id,
            )
    finally:
        file_path.unlink()
