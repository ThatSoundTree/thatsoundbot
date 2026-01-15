from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound, TelegramConflictError
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from loguru import logger
from thatsoundbot.utils.hashing import to_hgramid


IGNORABLE_ERRORS = {
    "query is too old and response timeout expired or query id is invalid",
    "query is too old",
    "response timeout expired",
    "query id is invalid",
    "message to edit not found",
    "message not found",
    "message to delete not found",
    "message can't be deleted",
    "message can't be edited",
    "bad request: message is not modified",
    "message is not modified",
    "message to pin not found",
    "chat not found",
    "user not found",
    "callback query is too old",
    "inline message expired",
}


def _extract_hgramid_from_update(update) -> str:
    if update.callback_query and update.callback_query.from_user:
        return to_hgramid(update.callback_query.from_user.id)
    elif update.message and update.message.from_user:
        return to_hgramid(update.message.from_user.id)
    elif update.inline_query and update.inline_query.from_user:
        return to_hgramid(update.inline_query.from_user.id)
    elif update.chosen_inline_result and update.chosen_inline_result.from_user:
        return to_hgramid(update.chosen_inline_result.from_user.id)
    return "unknown"


def create_error_router() -> Router:
    router = Router(name="error_handler")

    @router.error(ExceptionTypeFilter(TelegramBadRequest))
    async def telegram_bad_request_handler(event: ErrorEvent) -> None:
        exception = event.exception
        error_message = str(exception).lower()

        if any(ignorable in error_message for ignorable in IGNORABLE_ERRORS):
            hgramid = _extract_hgramid_from_update(event.update)
            hgramid_short = hgramid[:8] if isinstance(hgramid, str) else "unknown"

            logger.warning(
                "[{hgramid}] [tg_error] TelegramBadRequest: {error_msg}",
                hgramid=hgramid_short,
                error_msg=exception.message if hasattr(exception, "message") else str(exception)
            )
            return

        logger.warning(
            "[tg_error] Unhandled TelegramBadRequest: {error_msg}",
            error_msg=exception.message if hasattr(exception, "message") else str(exception)
        )

    @router.error(ExceptionTypeFilter(TelegramNotFound, TelegramConflictError))
    async def telegram_not_found_handler(event: ErrorEvent) -> None:
        exception = event.exception
        error_message = str(exception).lower()

        if any(ignorable in error_message for ignorable in IGNORABLE_ERRORS):
            hgramid = _extract_hgramid_from_update(event.update)
            hgramid_short = hgramid[:8] if isinstance(hgramid, str) else "unknown"

            logger.warning(
                "[{hgramid}] [tg_error] {error_type}: {error_msg}",
                hgramid=hgramid_short,
                error_type=type(exception).__name__,
                error_msg=exception.message if hasattr(exception, "message") else str(exception)
            )
            return

        logger.warning(
            "[tg_error] Unhandled {error_type}: {error_msg}",
            error_type=type(exception).__name__,
            error_msg=exception.message if hasattr(exception, "message") else str(exception)
        )

    return router
