from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from thatsoundbot.models.pipelines_view import TracksPipelineView
from thatsoundbot.settings import get_settings


def create_empty_tracks_article(tracks_pipeline: TracksPipelineView) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id="error_no_results",
        title=tracks_pipeline.empty_title,
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.empty_inline_text
        ),
    )

def create_channel_ad_query_result(tracks_pipeline: TracksPipelineView) -> InlineQueryResultArticle:
    settings = get_settings()
    return InlineQueryResultArticle(
        id="channel_ad",
        title=tracks_pipeline.channel_ad_text,
        url=settings.LOGS_CHANNEL_URL,
        input_message_content=InputTextMessageContent(
            message_text=tracks_pipeline.empty_inline_text
        )
    )
