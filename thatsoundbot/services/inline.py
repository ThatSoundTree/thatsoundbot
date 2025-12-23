from aiogram.types import InlineQueryResultArticle
from httpx import HTTPStatusError
from loguru import logger

from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.inline import create_error_result
from thatsoundbot.models import RecentTracksResponse, SpotifyTrack
from thatsoundbot.repositories.downloads import create_download_task
from thatsoundbot.repositories.sounds import get_recent_tracks


async def fetch_tracks(htelegram_id: str) -> RecentTracksResponse | Exception:
    """Fetch tracks with error handling, returns result or exception."""
    error: Exception
    try:
        result = await get_recent_tracks(htelegram_id)
        return result
    except Exception as error:
        return error


def handle_inline_error(error: Exception, htelegram_id: str) -> InlineQueryResultArticle:
    """Handle inline query errors and return appropriate error result."""
    if isinstance(error, HTTPStatusError) and error.response.status_code == 401:
        logger.info("User not authorized for Spotify: htelegram_id=%s", htelegram_id[:8])
        return create_error_result(TEXTS["inline"]["not_authorized"])

    logger.exception("Error handling inline query: %s", error)
    return create_error_result(TEXTS["inline"]["error"])


def parse_track_id(result_id: str) -> str | None:
    """Parse track ID from inline result ID."""
    if not result_id.startswith("track_"):
        return None
    parts = result_id.split("_")
    return parts[1] if len(parts) > 1 else None


async def get_track_by_id(htelegram_id: str, track_id: str) -> SpotifyTrack | None:
    """Get track by ID from recent tracks."""
    response = await fetch_tracks(htelegram_id)
    if isinstance(response, Exception):
        return None
    for track in response.tracks:
        if track.id == track_id:
            return track
    return None


async def create_track_download_task(track: SpotifyTrack, message_id: str | None) -> dict | Exception:
    """Create download task for track on external backend."""
    result = await create_download_task(track, message_id)
    return result
