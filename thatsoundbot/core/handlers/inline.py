from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.models.pipelines_view import PipelineView
from thatsoundbot.services.recent import get_recent_tracks

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle inline query requests."""
    logger.info("[{hgramid}] [callback] init", hgramid=hgramid[:8])

    tracks = await get_recent_tracks(hgramid=hgramid)
    if not tracks:
        logger.warning("[{hgramid}] [callback] empty tracks", hgramid=hgramid[:8])
        results = empty_inline_result(tracks_pipeline=pipeline.tracks)
        await inline_query.answer(results=results, cache_time=1)
        return

    results = [create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks]
    logger.info("[{hgramid}] [callback] len(results) == {len_results}", hgramid=hgramid[:8], len_results=len(results))
    await inline_query.answer(results=results, cache_time=0)  # type: ignore[arg-type]

#
# @router.chosen_inline_result()
# async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
#     """Handle chosen inline result and send track text."""
#     logger.info(
#         "Chosen inline result received: result_id={result_id}, query={query}, "
#         "inline_message_id={inline_message_id}",
#         result_id=chosen_result.result_id,
#         query=chosen_result.query,
#         inline_message_id=chosen_result.inline_message_id,
#     )
#
#     # Skip processing for empty tracks result (nothing should be sent)
#     if chosen_result.result_id == "error_no_results":
#         logger.info("Empty tracks result selected, skipping processing")
#         return
#
#     if not chosen_result.from_user or not chosen_result.bot:
#         logger.warning("Chosen inline result without from_user or bot")
#         return
#
#     track_id = parse_track_id(chosen_result.result_id)
#     if not track_id:
#         logger.warning("Invalid track ID in chosen result: %s", chosen_result.result_id)
#         return
#
#     telegram_id = chosen_result.from_user.id
#     htelegram_id = hash_telegram_id(telegram_id)
#     track = await get_track_by_id(htelegram_id, track_id)
#
#     if not track:
#         logger.warning("Track not found: track_id=%s", track_id)
#         return
#
#     message_id = chosen_result.inline_message_id
#     is_inline = bool(message_id)
#     chat_id = chosen_result.from_user.id
#
#     logger.info(
#         "Processing chosen inline result: track_id={track_id}, is_inline={is_inline}, chat_id={chat_id}",
#         track_id=track_id,
#         is_inline=is_inline,
#         chat_id=chat_id,
#     )
#
#     if message_id:
#         await chosen_result.bot.edit_message_text(
#             inline_message_id=message_id,
#             text="Downloading...",
#         )
#         logger.info("Edited inline message with 'Downloading...' text")
#     else:
#         logger.warning(
#             "Regular message via inline bot (inline_message_id=None) - "
#             "inline keyboard may not have been attached. Creating download task anyway."
#         )
#         message_id = None
#
#     result = await create_track_download_task(
#         track, htelegram_id, message_id, chosen_result.bot, chat_id, is_inline
#     )
#     if isinstance(result, Exception):
#         logger.error("Failed to create download task: %s", result)
#     else:
#         logger.info("Download task created successfully: task_id={task_id}", task_id=result.get("task_id") if isinstance(result, dict) else None)
#
#
# @router.message(F.text == "Downloading...", F.via_bot.is_not(None))
# async def inline_result_message_handler(message: Message) -> None:
#     """Handle message sent via inline query result."""
#     if not message.from_user or not message.bot:
#         return
#
#     if not message.via_bot or message.via_bot.id != message.bot.id:
#         return
#
#     telegram_id = message.from_user.id
#     htelegram_id = hash_telegram_id(telegram_id)
#
#     recent_tracks = await get_recent_tracks(htelegram_id)
#     if not recent_tracks.tracks:
#         return
#
#     track = recent_tracks.tracks[0] if recent_tracks.tracks else None
#     if not track:
#         return
#
#     message_id = str(message.message_id)
#     result = await create_track_download_task(
#         track, htelegram_id, message_id, message.bot, message.from_user.id, False
#     )
#     if isinstance(result, Exception):
#         logger.error("Failed to create download task: %s", result)
#

@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    """Handle callback from loading button in inline messages.

    This button is just a placeholder to ensure we get inline_message_id.
    We simply answer the callback to prevent "loading" state.
    """
    await callback.answer()
