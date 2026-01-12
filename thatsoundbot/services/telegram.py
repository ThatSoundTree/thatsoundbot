from aiogram.types import FSInputFile, InputMediaAudio
from loguru import logger

from thatsoundbot.core import  create_bot
from thatsoundbot.settings import get_settings


async def attach_audio_in_message(hgramid: str, inline_message_id: str, file_id: str):
    settings = get_settings()
    bot = create_bot(settings=settings)
    media = InputMediaAudio(media=file_id)
    await bot.edit_message_media(inline_message_id=inline_message_id, media=media)
    logger.success("[{hgramid}] [attach] success attached", hgramid=hgramid[:8])
    await bot.session.close()


async def backup_track(audio: FSInputFile, thumbnail: FSInputFile, caption: str) -> str:
    settings = get_settings()

    bot = create_bot(settings=settings)
    sent_message = await bot.send_audio(
        chat_id=settings.CACHE_CHANNEL,
        audio=audio,
        thumbnail =thumbnail,
        caption = caption
    )
    await bot.session.close()

    if not sent_message.audio:
        raise RuntimeError("Audio message was not sent")
    return sent_message.audio.file_id
