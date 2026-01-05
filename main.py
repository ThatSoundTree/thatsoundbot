import asyncio

from loguru import logger

from thatsoundbot.core import create_bot, create_dispatcher
from thatsoundbot.core.handlers import inline_router, integrations_router, start_router
from thatsoundbot.settings import get_settings


async def main() -> None:
    """Application entry point."""
    settings = get_settings()
    bot = create_bot(settings)
    dp = create_dispatcher()
    dp.include_router(start_router)
    dp.include_router(integrations_router)
    dp.include_router(inline_router)

    logger.info("Bot is starting...")

    bot_info = await bot.get_me()
    logger.info(
        "Bot connected successfully: @{username} (id: {id})",
        username=bot_info.username,
        id=bot_info.id,
    )

    logger.info("Starting polling...")
    await dp.start_polling(bot, drop_pending_updates=True)
    await bot.session.close()
    logger.info("Bot session closed")


if __name__ == "__main__":
    asyncio.run(main())
