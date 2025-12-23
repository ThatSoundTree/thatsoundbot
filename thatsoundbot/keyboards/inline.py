import httpx
from aiogram import Bot
from aiogram.types import BufferedInputFile, InlineQueryResultArticle, InlineQueryResultAudio, InputTextMessageContent

from thatsoundbot.handlers.messages.formatters import format_artists
from thatsoundbot.models import SpotifyTrack
from thatsoundbot.utils.audio import create_audio_file

_file_id_cache: dict[str, str] = {}


async def create_inline_result(track: SpotifyTrack, index: int, bot: Bot, chat_id: int) -> InlineQueryResultAudio:
    """Create inline query result for a track with audio file."""
    artists = format_artists(track.artists)

    if track.id in _file_id_cache:
        file_id = _file_id_cache[track.id]
    else:
        album_cover_data = None
        if track.album_cover_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(track.album_cover_url)
                if response.status_code == 200:
                    album_cover_data = response.content

        audio_buffer = await create_audio_file(track, album_cover_data)
        audio_file = BufferedInputFile(audio_buffer.getvalue(), filename=f"{track.id}.mp3")

        message = await bot.send_audio(
            chat_id=chat_id,
            audio=audio_file,
            disable_notification=True,
        )
        file_id = message.audio.file_id if message.audio else ""
        _file_id_cache[track.id] = file_id

        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)

    return InlineQueryResultAudio(
        id=f"track_{track.id}_{index}",
        audio_url=file_id,
        title=track.name,
        performer=artists,
    )


def create_error_result(message: str) -> InlineQueryResultArticle:
    """Create inline query result for error/empty state."""
    return InlineQueryResultArticle(
        id="error_no_results",
        title=message,
        description="Try again later",
        input_message_content=InputTextMessageContent(
            message_text=message,
            parse_mode="HTML",
        ),
    )
