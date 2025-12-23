from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from thatsoundbot.handlers.messages.formatters import format_artists, format_track_text
from thatsoundbot.models import SpotifyTrack


def create_inline_result(track: SpotifyTrack, index: int) -> InlineQueryResultArticle:
    """Create inline query result for a track."""
    artists = format_artists(track.artists)
    title = f"{track.name} - {artists}"

    description_parts = []
    if track.album:
        description_parts.append(track.album)
    if track.played_at:
        description_parts.append(f"Played: {track.played_at}")
    description = " • ".join(description_parts) if description_parts else None

    return InlineQueryResultArticle(
        id=f"track_{track.id}_{index}",
        title=title,
        description=description,
        thumbnail_url=track.album_cover_url,
        input_message_content=InputTextMessageContent(
            message_text=format_track_text(track),
            parse_mode="HTML",
        ),
    )


def create_error_result(message: str) -> InlineQueryResultArticle:
    """Create inline query result for error/empty state."""
    return InlineQueryResultArticle(
        id="error_no_results",
        title=message,
        description="Try again later",
        input_message_content=InputTextMessageContent(
            message_text=message,
            parse_mode="HTML",
        ),
    )
