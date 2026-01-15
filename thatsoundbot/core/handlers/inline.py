import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.core.models.pipelines_view import PipelineView
from thatsoundbot.db.redis import RedisService
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.services.tsripper import process_chosen_result

router = Router(name="inline")


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, redis: RedisService, hgramid: str, pipeline: PipelineView) -> None:
    """Handle inline query requests."""
    logger.info("[{hgramid}] [inline] init", hgramid=hgramid[:8])

    tracks = await get_recent_tracks(hgramid=hgramid)
    if not (tracks.yandex_music or tracks.spotify):
        logger.warning("[{hgramid}] [inline] empty tracks", hgramid=hgramid[:8])
        results = empty_inline_result(tracks_pipeline=pipeline.tracks)
        await inline_query.answer(results=results, cache_time=5)  # type: ignore[arg-type]
        return

    results = []
    spotify_tasks = [
        create_track_item(redis=redis, track=track, tracks_pipeline=pipeline.tracks)
        for track in tracks.spotify
    ]

    yandex_music_tasks = [
        create_track_item(redis=redis, track=track, tracks_pipeline=pipeline.tracks)
        for track in tracks.yandex_music
    ]

    spotify_items, yandex_music_items = await asyncio.gather(
        asyncio.gather(*spotify_tasks),
        asyncio.gather(*yandex_music_tasks),
    )

    logger.info(
        "[{hgramid}] [inline] prepared yandex_music={len_yandex} and spotify={len_spotify}",
        hgramid=hgramid[:8], len_yandex=len(yandex_music_items),
        len_spotify=len(spotify_items)
    )
    results.extend(spotify_items)
    results.extend(yandex_music_items)
    await inline_query.answer(results=results, cache_time=3)  # type: ignore[arg-type]


@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    """Handle loading button callback from inline messages."""
    logger.info("[callback] loading button clicked, data=%s", callback.data)
    await callback.answer()


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult, redis: RedisService, hgramid: str) -> None:
    """Handle chosen inline result and send track text."""
    bot = chosen_result.bot
    if not (bot and chosen_result.inline_message_id):
        raise RuntimeError

    await process_chosen_result(redis=redis, bot=bot, chosen_result=chosen_result, hgramid=hgramid, )
