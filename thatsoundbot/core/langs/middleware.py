from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery, ChosenInlineResult

from thatsoundbot.settings import get_pipelines


class PipelineMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        language_code = None
        if isinstance(event, (Message, CallbackQuery, InlineQuery, ChosenInlineResult)) and event.from_user:
            language_code = event.from_user.language_code

        pipelines = get_pipelines()
        pipeline = pipelines[language_code] if language_code else pipelines.RU

        data["pipeline"] = pipeline

        return await handler(event, data)
