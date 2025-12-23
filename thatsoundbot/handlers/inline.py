import asyncio

import httpx
from aiogram import Router
from aiogram.types import BufferedInputFile, ChosenInlineResult, InlineQuery, InlineQueryResultArticle, InputMediaAudio
from httpx import HTTPStatusError
from loguru import logger

from thatsoundbot.backend.api import get_recent_tracks
from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.inline import create_error_result, create_inline_result
from thatsoundbot.models import RecentTracksResponse, SpotifyTrack
from thatsoundbot.utils.audio import create_audio_file
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="inline")


async def _fetch_tracks_safe(htelegram_id: str) -> RecentTracksResponse | Exception:
    """Fetch tracks with error handling, returns result or exception."""
    result = await get_recent_tracks(htelegram_id)
    return result


def _handle_inline_error(error: Exception, htelegram_id: str) -> InlineQueryResultArticle:
    """Handle inline query errors and return appropriate error result."""
    if isinstance(error, HTTPStatusError) and error.response.status_code == 401:
        logger.info("User not authorized for Spotify: htelegram_id=%s", htelegram_id[:8])
        return create_error_result(TEXTS["inline"]["not_authorized"])

    logger.exception("Error handling inline query: %s", error)
    return create_error_result(TEXTS["inline"]["error"])


def _parse_track_id(result_id: str) -> str | None:
    """Parse track ID from inline result ID."""
    if not result_id.startswith("track_"):
        return None
    parts = result_id.split("_")
    return parts[1] if len(parts) > 1 else None


async def _get_track_by_id(htelegram_id: str, track_id: str) -> SpotifyTrack | None:
    """Get track by ID from recent tracks."""
    response = await _fetch_tracks_safe(htelegram_id)
    if isinstance(response, Exception):
        return None
    for track in response.tracks:
        if track.id == track_id:
            return track
    return None


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery) -> None:
    """Handle inline query requests."""
    if not inline_query.from_user:
        await inline_query.answer(results=[], cache_time=1)
        return

    telegram_id = inline_query.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)

    response = await _fetch_tracks_safe(htelegram_id)
    if isinstance(response, Exception):
        error_result = _handle_inline_error(response, htelegram_id)
        await inline_query.answer(results=[error_result], cache_time=1)
        return

    if not response.tracks:
        error_result = create_error_result(TEXTS["inline"]["no_tracks"])
        await inline_query.answer(results=[error_result], cache_time=1)
        return

    bot = inline_query.bot
    if not bot:
        await inline_query.answer(results=[], cache_time=1)
        return

    chat_id = inline_query.from_user.id
    results = await asyncio.gather(
        *[create_inline_result(track, index, bot, chat_id) for index, track in enumerate(response.tracks)]
    )

    await inline_query.answer(results=results, cache_time=1)  # type: ignore[arg-type]


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
    """Handle chosen inline result and send zero-duration audio file."""
    if not chosen_result.from_user or not chosen_result.bot:
        return

    track_id = _parse_track_id(chosen_result.result_id)
    if not track_id:
        logger.warning("Invalid track ID in chosen result: %s", chosen_result.result_id)
        return

    telegram_id = chosen_result.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)
    track = await _get_track_by_id(htelegram_id, track_id)

    if not track:
        logger.warning("Track not found: track_id=%s", track_id)
        return

    album_cover_data = None
    if track.album_cover_url:
        async with httpx.AsyncClient() as client:
            response = await client.get(track.album_cover_url)
            if response.status_code == 200:
                album_cover_data = response.content

    audio_buffer = await create_audio_file(track, album_cover_data)
    audio_file = BufferedInputFile(audio_buffer.getvalue(), filename=f"{track.id}.mp3")

    if chosen_result.inline_message_id:
        await chosen_result.bot.edit_message_media(
            inline_message_id=chosen_result.inline_message_id,
            media=InputMediaAudio(
                media=audio_file,
                title=track.name,
                performer=", ".join(track.artists) if track.artists else "Unknown Artist",
                caption="Loading...",
            ),
        )
    else:
        await chosen_result.bot.send_audio(
            chat_id=chosen_result.from_user.id,
            audio=audio_file,
            title=track.name,
            performer=", ".join(track.artists) if track.artists else "Unknown Artist",
            caption="Loading...",
        )
