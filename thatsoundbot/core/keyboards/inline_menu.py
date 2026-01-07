from thatsoundbot.models.pipelines_view import TracksPipelineView
from thatsoundbot.models.tsapi import TrackView
from thatsoundbot.settings import get_settings
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)



def create_empty_tracks_article(tracks_pipeline) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id="error_no_results",
        title=tracks_pipeline.empty_title,
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.empty_inline_text
        ),
    )


def create_channel_ad_query_result(tracks_pipeline) -> InlineQueryResultArticle:
    settings = get_settings()
    return InlineQueryResultArticle(
        id="channel_ad",
        title=tracks_pipeline.channel_ad_text,
        url=settings.LOGS_CHANNEL_URL,
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.empty_inline_text
        ),
    )


def empty_inline_result(tracks_pipeline) -> list[InlineQueryResultArticle]:
    return [
        create_empty_tracks_article(tracks_pipeline),
        create_channel_ad_query_result(tracks_pipeline),
    ]


def create_loading_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏳", callback_data="loading")]
        ]
    )


def create_track_item(track: TrackView, tracks_pipeline: TracksPipelineView) -> InlineQueryResultArticle:
    result = InlineQueryResultArticle(
        id=track.url,
        title=track.name,
        description=", ".join(track.artists) if track.artists else "Unknown Artist",
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.loading_text,
        ),
        reply_markup=create_loading_markup()
    )

    if track.album_cover_url:
        result.thumbnail_url = track.album_cover_url

    return result