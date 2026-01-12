import random
import string

from thatsoundbot.core.models.pipelines_view import TracksPipelineView
from thatsoundbot.core.models.tsapi import TrackView
from thatsoundbot.settings import get_settings, get_tsripper_settings
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from thatsoundbot.utils.http_client import extract_domain


def create_empty_tracks_article(tracks_pipeline) -> InlineQueryResultArticle:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=15))
    return InlineQueryResultArticle(
        id=random_string,
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


def create_track_item(track: TrackView, tracks_pipeline: TracksPipelineView, inline_query_id: str, provider: int) -> InlineQueryResultArticle:
    tsripper_settings = get_tsripper_settings()

    if not tsripper_settings.IN_USE:
        unique_id = f"{inline_query_id[:6]}_{track.url}"
    else:
        unique_id = f"{inline_query_id[:6]}_{track.id}_{provider}"

    result = InlineQueryResultArticle(
        id=unique_id,
        title=track.name,
        description=", ".join(track.artists) if track.artists else "Unknown Artist",
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.loading_text,
        ),
        reply_markup=create_loading_markup(),
        url=extract_domain(track.url),
    )

    if track.album_cover_url:
        result.thumbnail_url = track.album_cover_url

    return result
