import asyncio

from loguru import logger

from thatsoundbot.core import create_bot, create_dispatcher
from thatsoundbot.handlers import integrations_router, start_router
from thatsoundbot.settings import get_settings


async def main() -> None:
    """Application entry point."""
    settings = get_settings()
    bot = create_bot(settings)
    dp = create_dispatcher()
    dp.include_router(start_router)
    dp.include_router(integrations_router)

    logger.info("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
