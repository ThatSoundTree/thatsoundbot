import asyncio

from aiogram import Router
from aiogram.types import ChosenInlineResult, InlineQuery, InlineQueryResultArticle
from httpx import HTTPStatusError
from loguru import logger

from thatsoundbot.backend.api import get_recent_tracks
from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.inline import create_error_result, create_inline_result
from thatsoundbot.models import RecentTracksResponse
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="inline")


async def _fetch_tracks_safe(htelegram_id: str) -> RecentTracksResponse | Exception:
    """Fetch tracks with error handling, returns result or exception."""
    try:
        return await get_recent_tracks(htelegram_id)
    except Exception as e:
        return e


def _handle_inline_error(error: Exception, htelegram_id: str) -> InlineQueryResultArticle:
    """Handle inline query errors and return appropriate error result."""
    if isinstance(error, HTTPStatusError) and error.response.status_code == 401:
        logger.info("User not authorized for Spotify: htelegram_id=%s", htelegram_id[:8])
        return create_error_result(TEXTS["inline"]["not_authorized"])

    logger.exception("Error handling inline query: %s", error)
    return create_error_result(TEXTS["inline"]["error"])


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
    """Handle chosen inline result (when user selects a track)."""
    logger.info(f"User selected inline result: {chosen_result.result_id}")
