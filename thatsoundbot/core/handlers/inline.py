from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from thatsoundbot.core.keyboards.inline_menu import empty_inline_result, create_track_item
from thatsoundbot.core.models.pipelines_view import PipelineView
from thatsoundbot.services.recent import get_recent_tracks
from thatsoundbot.services.telegram import attach_audio_in_message
from thatsoundbot.services.tsripper import scrobble_track, fetch_file_id_periodically, process_backup_track
from thatsoundbot.settings import get_settings, get_tsripper_settings, TSAPISettings

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
    spotify_items = [create_track_item(track=track, tracks_pipeline=pipeline.tracks, inline_query_id=inline_query.id, provider=TSAPISettings.Providers.Spotify.value) for track in tracks.spotify]
    yandex_music_items = [create_track_item(track=track, tracks_pipeline=pipeline.tracks, inline_query_id=inline_query.id, provider=TSAPISettings.Providers.YandexMusic.value) for track in tracks.yandex_music]


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

    bot = chosen_result.bot
    if not (bot and chosen_result.inline_message_id):
        raise RuntimeError

    if not tsripper_settings.IN_USE:
        track_url = chosen_result.result_id
        if "_" in track_url:
            track_url = track_url.split("_", 1)[1]

        await bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text=track_url,
        )
        return

    raw_scrobble_info = chosen_result.result_id.split("_")
    track_id = raw_scrobble_info[-2]
    track_provider = raw_scrobble_info[-1]

    scrobble_response = await scrobble_track(hgramid=hgramid, track_id=track_id, track_provider=track_provider)

    if isinstance(scrobble_response, str):
        logger.info("[{hgramid}] [scrobble] using cached track", hgramid=hgramid[:8])
        file_id = scrobble_response
    elif isinstance(scrobble_response, UUID):
        logger.info("[{hgramid}] [scrobble] caching new track", hgramid=hgramid[:8])
        file_id = await process_backup_track(
            hgramid=hgramid,
            scrobble_id=scrobble_response,
            track_id_with_provider=f"{track_id}!@#{track_provider}"
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
