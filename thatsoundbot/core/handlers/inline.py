import asyncio
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.core.models.pipelines_view import PipelineView
from thatsoundbot.db import RedisClient
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.services.telegram import attach_audio_in_message
from thatsoundbot.services.tsripper import scrobble_track, process_backup_track
from thatsoundbot.settings import get_tsripper_settings, TSAPISettings

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
    spotify_items = [await create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks.spotify]
    yandex_music_items = [await create_track_item(track=track, tracks_pipeline=pipeline.tracks) for track in tracks.yandex_music]

    logger.info(
        "[{hgramid}] [inline] prepared yandex_music={len_yandex} and spotify={len_spotify}",
        hgramid=hgramid[:8], len_yandex=len(yandex_music_items),
        len_spotify=len(spotify_items)
    )
    results.extend(spotify_items)
    results.extend(yandex_music_items)
    await inline_query.answer(results=results, cache_time=3)  # type: ignore[arg-type]


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult, hgramid: str) -> None:
    """Handle chosen inline result and send track text."""
    tsripper_settings = get_tsripper_settings()
    redis = RedisClient.current()

    bot = chosen_result.bot
    if not (bot and chosen_result.inline_message_id):
        raise RuntimeError

    selected_track = await redis.get_result_query(result_id=chosen_result.result_id)

    if not tsripper_settings.IN_USE:
        if not selected_track:
            logger.error(
                "[{hgramid}] [scrobble] redis cleared result=[{result_id}] earlier",
                hgramid=hgramid[:8],
                result_id=chosen_result.result_id
            )

        await bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text=selected_track.url,
        )
        return

    scrobble_response = await scrobble_track(hgramid=hgramid, selected_track=selected_track)

    if isinstance(scrobble_response, str):
        logger.info("[{hgramid}] [scrobble] using cached track", hgramid=hgramid[:8])
        file_id = scrobble_response
    elif isinstance(scrobble_response, UUID):
        logger.info("[{hgramid}] [scrobble] caching new track", hgramid=hgramid[:8])
        file_id = await process_backup_track(
            hgramid=hgramid,
            scrobble_id=scrobble_response,
            track=selected_track,
        )
    else:
        return

    await attach_audio_in_message(
        hgramid=hgramid,
        inline_message_id=chosen_result.inline_message_id,
        file_id=file_id
    )


@router.callback_query(F.data == "loading")
async def loading_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
