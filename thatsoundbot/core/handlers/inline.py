from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.core.models.pipelines_view import PipelineView
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.settings import get_settings

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle inline query requests."""
    logger.info("[{hgramid}] [inline] init", hgramid=hgramid[:8])

    tracks = await get_recent_tracks(hgramid=hgramid)
    if not (tracks.yandex_music or tracks.spotify):
        logger.warning("[{hgramid}] [inline] empty tracks", hgramid=hgramid[:8])
        results = empty_inline_result(tracks_pipeline=pipeline.tracks)
        await inline_query.answer(results=results, cache_time=5)  # type: ignore[arg-type]
        return

    results = []
    spotify_items = [create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks.spotify]
    yandex_music_items = [create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks.yandex_music]


    logger.info(
        "[{hgramid}] [inline] prepared yandex_music={len_yandex} and spotify={len_spotify}",
        hgramid=hgramid[:8], len_yandex=len(yandex_music_items),
        len_spotify=len(spotify_items)
    )
    results.extend(spotify_items)
    results.extend(yandex_music_items)
    await inline_query.answer(results=results, cache_time=3)  # type: ignore[arg-type]


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult) -> None:
    """Handle chosen inline result and send track text."""
    settings = get_settings()

    bot = chosen_result.bot
    if not settings.USE_TSRIPPER and bot:
        track_url = chosen_result.result_id
        if "_" in track_url:
            track_url = track_url.split("_", 1)[1]

        await bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text=track_url,
        )

@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
