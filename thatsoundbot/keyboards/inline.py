from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from thatsoundbot.models import SpotifyTrack


async def create_inline_result(track: SpotifyTrack, index: int, bot, chat_id: int) -> InlineQueryResultArticle:
    """Create inline query result with track metadata text."""
    artists = ", ".join(track.artists) if track.artists else "Unknown Artist"

    result = InlineQueryResultArticle(
        id=f"track_{track.id}_{index}",
        title=track.name,
        description=artists,
        input_message_content=InputTextMessageContent(
            message_text="Loading...",
        ),
    )

    if track.album_cover_url:
        result.thumbnail_url = track.album_cover_url

    return result


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
