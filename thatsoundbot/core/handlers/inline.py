from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery, Message
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import create_empty_tracks_article, create_channel_ad_query_result
from thatsoundbot.models.pipelines_view import PipelineView
from thatsoundbot.services.inline import (
    create_track_download_task,
    get_track_by_id,
    parse_track_id,
)
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle inline query requests."""
    logger.info("[{hgramid}] [callback] init")

    telegram_id = inline_query.from_user.id


    tracks = await get_recent_tracks(hgramid=hgramid)
    tracks = []
    if not tracks:
        logger.warning("[{hgramid}] [callback] empty tracks", hgramid=hgramid[:8])
        empty_result = create_empty_tracks_article(tracks_pipeline=pipeline.tracks)
        empty_result2 = create_channel_ad_query_result(tracks_pipeline=pipeline.tracks)
        await inline_query.answer(results=[empty_result,empty_result2], cache_time=1)
        return
    #
    # if not response.tracks:
    #     logger.info(
    #         "No tracks found for inline query: htelegram_id={htelegram_id}",
    #         htelegram_id=htelegram_id[:8],
    #     )
    #     error_result = create_error_result(TEXTS["inline"]["no_tracks"])
    #     await inline_query.answer(results=[error_result], cache_time=1)
    #     return
    #
    # results = [
    #     create_inline_result(track, index) for index, track in enumerate(response.tracks)
    # ]
    #
    # logger.info(
    #     "Sending {count} inline results: htelegram_id={htelegram_id}",
    #     count=len(results),
    #     htelegram_id=htelegram_id[:8],
    # )
    #
    # await inline_query.answer(results=results, cache_time=0)  # type: ignore[arg-type]
    #

@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
    """Handle chosen inline result and send track text."""
    logger.info(
        "Chosen inline result received: result_id={result_id}, query={query}, "
        "inline_message_id={inline_message_id}",
        result_id=chosen_result.result_id,
        query=chosen_result.query,
        inline_message_id=chosen_result.inline_message_id,
    )

    # Skip processing for empty tracks result (nothing should be sent)
    if chosen_result.result_id == "error_no_results":
        logger.info("Empty tracks result selected, skipping processing")
        return

    if not chosen_result.from_user or not chosen_result.bot:
        logger.warning("Chosen inline result without from_user or bot")
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

    message_id = chosen_result.inline_message_id
    is_inline = bool(message_id)
    chat_id = chosen_result.from_user.id

    logger.info(
        "Processing chosen inline result: track_id={track_id}, is_inline={is_inline}, chat_id={chat_id}",
        track_id=track_id,
        is_inline=is_inline,
        chat_id=chat_id,
    )

    if message_id:
        await chosen_result.bot.edit_message_text(
            inline_message_id=message_id,
            text="Downloading...",
        )
        logger.info("Edited inline message with 'Downloading...' text")
    else:
        logger.warning(
            "Regular message via inline bot (inline_message_id=None) - "
            "inline keyboard may not have been attached. Creating download task anyway."
        )
        message_id = None

    result = await create_track_download_task(
        track, htelegram_id, message_id, chosen_result.bot, chat_id, is_inline
    )
    if isinstance(result, Exception):
        logger.error("Failed to create download task: %s", result)
    else:
        logger.info("Download task created successfully: task_id={task_id}", task_id=result.get("task_id") if isinstance(result, dict) else None)


@router.message(F.text == "Downloading...", F.via_bot.is_not(None))
async def inline_result_message_handler(message: Message) -> None:
    """Handle message sent via inline query result."""
    if not message.from_user or not message.bot:
        return

    if not message.via_bot or message.via_bot.id != message.bot.id:
        return

    telegram_id = message.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)

    recent_tracks = await get_recent_tracks(htelegram_id)
    if not recent_tracks.tracks:
        return

    track = recent_tracks.tracks[0] if recent_tracks.tracks else None
    if not track:
        return

    message_id = str(message.message_id)
    result = await create_track_download_task(
        track, htelegram_id, message_id, message.bot, message.from_user.id, False
    )
    if isinstance(result, Exception):
        logger.error("Failed to create download task: %s", result)


@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    """Handle callback from loading button in inline messages.

    This button is just a placeholder to ensure we get inline_message_id.
    We simply answer the callback to prevent "loading" state.
    """
    await callback.answer()
