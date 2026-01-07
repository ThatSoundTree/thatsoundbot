from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.models.pipelines_view import PipelineView
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.settings import get_settings

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle inline query requests."""
    logger.info("[{hgramid}] [inline] init", hgramid=hgramid[:8])

    tracks = await get_recent_tracks(hgramid=hgramid)
    if not tracks:
        logger.warning("[{hgramid}] [inline] empty tracks", hgramid=hgramid[:8])
        results = empty_inline_result(tracks_pipeline=pipeline.tracks)
        await inline_query.answer(results=results, cache_time=5)
        return

    results = [create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks]
    logger.info("[{hgramid}] [inline] len(results) == {len_results}", hgramid=hgramid[:8], len_results=len(results))

    await inline_query.answer(results=results, cache_time=3)  # type: ignore[arg-type]


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
    """Handle chosen inline result and send track text."""
    settings = get_settings()

    if not settings.USE_TSRIPPER:
        await chosen_result.bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text=chosen_result.result_id,
        )

@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
