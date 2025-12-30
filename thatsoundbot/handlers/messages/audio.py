from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaAudio, InputMediaDocument
from loguru import logger

from thatsoundbot.utils.telegram import extract_file_id


async def handle_inline_audio_message(
    bot: Bot, file_path: Path, filename: str, message_id: str, temp_channel: str, track_id: str
) -> None:
    """Handle inline message update with audio."""
    audio_input = FSInputFile(file_path, filename=filename)
    caption = f"spotify:{track_id}" if track_id else None
    logger.info("Sending file to temp channel: track_id={track_id}, caption={caption}", track_id=track_id, caption=caption)
    sent_message = await bot.send_document(chat_id=temp_channel, document=audio_input, caption=caption)

    file_id = extract_file_id(sent_message)
    if not file_id:
        return

    media = (
        InputMediaAudio(media=file_id)
        if sent_message.audio or sent_message.document
        else InputMediaDocument(media=file_id)
    )

    await bot.edit_message_media(inline_message_id=message_id, media=media)


async def handle_regular_audio_message(
    bot: Bot, file_path: Path, filename: str, chat_id: int, message_id: str
) -> None:
    """Handle regular message update with audio."""
    audio_input = FSInputFile(file_path, filename=filename)
    sent_message = await bot.send_audio(chat_id=777000, audio=audio_input)

    file_id = extract_file_id(sent_message)
    if not file_id:
        await bot.delete_message(chat_id=777000, message_id=sent_message.message_id)
        return

    await bot.edit_message_media(
        chat_id=chat_id, message_id=int(message_id), media=InputMediaAudio(media=file_id)
    )
    await bot.delete_message(chat_id=777000, message_id=sent_message.message_id)
