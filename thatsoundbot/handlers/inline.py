from aiogram import Router
from aiogram.types import ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.inline import create_error_result, create_inline_result
from thatsoundbot.services.inline import (
    fetch_tracks,
    get_track_by_id,
    handle_inline_error,
    parse_track_id,
)
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery) -> None:
    """Handle inline query requests."""
    if not inline_query.from_user:
        await inline_query.answer(results=[], cache_time=1)
        return

    telegram_id = inline_query.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)

    response = await fetch_tracks(htelegram_id)
    if isinstance(response, Exception):
        error_result = handle_inline_error(response, htelegram_id)
        await inline_query.answer(results=[error_result], cache_time=1)
        return

    if not response.tracks:
        error_result = create_error_result(TEXTS["inline"]["no_tracks"])
        await inline_query.answer(results=[error_result], cache_time=1)
        return

    results = [
        create_inline_result(track, index) for index, track in enumerate(response.tracks)
    ]

    await inline_query.answer(results=results, cache_time=1)  # type: ignore[arg-type]


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
    """Handle chosen inline result and send track text."""
    if not chosen_result.from_user or not chosen_result.bot:
        return

    track_id = parse_track_id(chosen_result.result_id)
    if not track_id:
        logger.warning("Invalid track ID in chosen result: %s", chosen_result.result_id)
        return

    telegram_id = chosen_result.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)
    track = await get_track_by_id(htelegram_id, track_id)

    if not track:
        logger.warning("Track not found: track_id=%s", track_id)
        return

    if chosen_result.inline_message_id:
        await chosen_result.bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text="Loading...",
        )
    else:
        await chosen_result.bot.send_message(
            chat_id=chosen_result.from_user.id,
            text="Loading...",
        )
