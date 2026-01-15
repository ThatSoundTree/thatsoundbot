from uuid import uuid4

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaAudio
from loguru import logger

from thatsoundbot.core.models.tsapi import TrackView
from thatsoundbot.settings import get_settings, TSAPISettings


async def attach_audio_in_message(bot: Bot, hgramid: str, inline_message_id: str, file_id: str):
    media = InputMediaAudio(media=file_id)
    await bot.edit_message_media(inline_message_id=inline_message_id, media=media)
    logger.success("[{hgramid}] [attach] success attached", hgramid=hgramid[:8])


async def backup_track(bot: Bot, audio: FSInputFile, thumbnail: FSInputFile, caption: str) -> str | None:
    settings = get_settings()

    sent_message = await bot.send_audio(
        chat_id=settings.CACHE_CHANNEL,
        audio=audio,
        thumbnail=thumbnail,
        caption=caption
    )

    if not sent_message.audio:
        logger.error("[backup] Failed to send message")
        return None

    return sent_message.audio.file_id


def unique_result_id() -> str:
    return uuid4().hex


def create_caption(track: TrackView) -> str:
    provider_enum = TSAPISettings.Providers(track.provider)
    caption = f"{provider_enum.name}:{track.id}"
    return caption


def create_telegram_filename(track: TrackView) -> str:
    artists = ", ".join(track.artists)
    return f"{artists} - {track.name}"
