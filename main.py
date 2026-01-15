import asyncio
import os
import sys
from loguru import logger

from thatsoundbot.core import create_bot, create_dispatcher
from thatsoundbot.core.handlers import inline_router, integrations_router
from thatsoundbot.db import RedisClient
from thatsoundbot.settings import get_settings
from thatsoundbot.utils.http_client import HttpClient

log_level = os.getenv("TELEGRAM_BOT_LOG_LEVEL", "INFO")
logger.remove()
logger.add(sys.stderr, level=log_level)



async def main() -> None:
    """Application entry point."""
    settings = get_settings()
    bot = create_bot(settings)
    dp = create_dispatcher()
    dp.include_router(integrations_router)
    dp.include_router(inline_router)

    logger.info("Starting application")
    HttpClient.startup()
    await RedisClient.startup()

    bot_info = await bot.get_me()
    logger.info(
        "Bot connected successfully: @{username} (id: {id})",
        username=bot_info.username,
        id=bot_info.id,
    )

    logger.info("Starting polling...")
    await dp.start_polling(bot, drop_pending_updates=True)

    logger.info("Shutting down application...")
    await bot.session.close()
    await HttpClient.shutdown()
    await RedisClient.shutdown()


    logger.info("Bot session closed")


if __name__ == "__main__":
    asyncio.run(main())
