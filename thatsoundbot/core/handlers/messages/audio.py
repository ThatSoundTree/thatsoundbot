import tempfile
from pathlib import Path
from typing import Optional

from aiogram import Bot
from aiogram.types import BufferedInputFile, FSInputFile, InputMedia, InputMediaAudio, InputMediaDocument
from loguru import logger

from thatsoundbot.utils.telegram import extract_file_id


async def handle_inline_audio_message(
    bot: Bot,
    file_path: Path,
    filename: str,
    message_id: str,
    temp_channel: str,
    track_id: str,
    thumbnail: Optional[bytes] = None,
) -> None:
    """Handle inline message update with audio."""
    audio_input = FSInputFile(file_path, filename=filename)
    caption = f"spotify:{track_id}" if track_id else None

    # Prepare thumbnail if available - Telegram doesn't extract from MP3 metadata!
    thumbnail_input = None
    thumbnail_temp_file = None

    if thumbnail:
        # Validate thumbnail is valid JPEG
        if thumbnail.startswith(b'\xff\xd8'):
            # Save thumbnail to temp file for better compatibility with Telegram
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(thumbnail)
                thumbnail_temp_file = Path(tmp_file.name)

            thumbnail_input = FSInputFile(thumbnail_temp_file, filename="thumbnail.jpg")
        else:
            logger.warning("Thumbnail is not a valid JPEG file (doesn't start with JPEG header)")
    else:
        logger.warning("No thumbnail provided for inline audio message")

    # Send as AUDIO (not document) with thumbnail to get proper file_id with thumbnail
    # This is crucial - Telegram needs thumbnail at initial send, not just when editing
    sent_message = await bot.send_audio(
        chat_id=temp_channel,
        audio=audio_input,
        caption=caption,
        thumbnail=thumbnail_input,
    )

    file_id = extract_file_id(sent_message)
    if not file_id:
        logger.error("Failed to extract file_id from sent message")
        if thumbnail_temp_file and thumbnail_temp_file.exists():
            thumbnail_temp_file.unlink()
        return

    # For edit_message_media, we MUST use InputFile, not file_id string
    # InputMediaAudio.thumbnail expects InputFile instance, not file_id string
    media_thumbnail = None

    # Always use the thumbnail input file (FSInputFile) for edit_message_media
    # Telegram doesn't accept file_id strings for thumbnail in InputMediaAudio
    if thumbnail_input and thumbnail:
        # Use the same thumbnail file we used for sending
        if thumbnail_temp_file and thumbnail_temp_file.exists():
            media_thumbnail = FSInputFile(thumbnail_temp_file, filename="thumbnail.jpg")
        else:
            if isinstance(thumbnail_input, FSInputFile):
                media_thumbnail = thumbnail_input
            else:
                media_thumbnail = BufferedInputFile(thumbnail, filename="thumbnail.jpg")

    # Create media with thumbnail for inline message
    media: InputMedia
    if sent_message.audio:
        media = InputMediaAudio(media=file_id, thumbnail=media_thumbnail) if media_thumbnail else InputMediaAudio(media=file_id)
    elif sent_message.document:
        media = InputMediaAudio(media=file_id, thumbnail=media_thumbnail) if media_thumbnail else InputMediaAudio(media=file_id)
    else:
        media = InputMediaDocument(media=file_id)

    await bot.edit_message_media(inline_message_id=message_id, media=media)

    # Clean up temp file if created
    if thumbnail_temp_file and thumbnail_temp_file.exists():
        thumbnail_temp_file.unlink()


async def handle_regular_audio_message(
    bot: Bot,
    file_path: Path,
    filename: str,
    chat_id: int,
    message_id: str,
    thumbnail: Optional[bytes] = None,
) -> None:
    """Handle regular message update with audio."""
    audio_input = FSInputFile(file_path, filename=filename)

    # Prepare thumbnail if available - Telegram doesn't extract from MP3 metadata!
    thumbnail_input = None
    thumbnail_temp_file = None

    if thumbnail:
        # Validate thumbnail is valid JPEG
        if thumbnail.startswith(b'\xff\xd8'):
            # Save to temp file for better compatibility
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(thumbnail)
                thumbnail_temp_file = Path(tmp_file.name)

            thumbnail_input = FSInputFile(thumbnail_temp_file, filename="thumbnail.jpg")
        else:
            logger.warning("Thumbnail is not a valid JPEG file (doesn't start with JPEG header)")

    sent_message = await bot.send_audio(
        chat_id=777000,
        audio=audio_input,
        thumbnail=thumbnail_input,
    )

    file_id = extract_file_id(sent_message)
    if not file_id:
        await bot.delete_message(chat_id=777000, message_id=sent_message.message_id)
        return

    # For editing, we MUST use InputFile, not file_id string
    # InputMediaAudio.thumbnail expects InputFile instance, not file_id string
    media_thumbnail = None
    thumbnail_temp_file_edit = None

    if thumbnail:
        # Always save thumbnail to temp file and use FSInputFile for edit_message_media
        # Telegram doesn't accept file_id strings for thumbnail in InputMediaAudio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(thumbnail)
            thumbnail_temp_file_edit = Path(tmp_file.name)

        media_thumbnail = FSInputFile(thumbnail_temp_file_edit, filename="thumbnail.jpg")

    media = InputMediaAudio(media=file_id, thumbnail=media_thumbnail) if media_thumbnail else InputMediaAudio(media=file_id)

    await bot.edit_message_media(
        chat_id=chat_id, message_id=int(message_id), media=media
    )

    # Clean up temp file if created
    if thumbnail_temp_file_edit and thumbnail_temp_file_edit.exists():
        thumbnail_temp_file_edit.unlink()

    await bot.delete_message(chat_id=777000, message_id=sent_message.message_id)
