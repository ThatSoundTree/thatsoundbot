from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from thatsoundbot.core.models import SpotifyTrack


def create_inline_result(track: SpotifyTrack, index: int) -> InlineQueryResultArticle:
    """Create inline query result with track metadata text.

    Note: We add an inline keyboard to ensure we get inline_message_id
    even when the message is sent as a regular message (not inline).
    This allows the bot to edit the message later.
    """
    artists = ", ".join(track.artists) if track.artists else "Unknown Artist"

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏳ Загрузка...", callback_data="loading")]
        ]
    )

    result = InlineQueryResultArticle(
        id=f"track_{track.id}_{index}",
        title=track.name,
        description=artists,
        input_message_content=InputTextMessageContent(
            message_text="Downloading...",
        ),
        reply_markup=reply_markup,
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
