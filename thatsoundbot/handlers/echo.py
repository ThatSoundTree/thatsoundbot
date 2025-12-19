from aiogram import Router
from aiogram.types import Message
from aiogram.utils.markdown import hbold

router = Router(name="echo")


@router.message()
async def echo_handler(message: Message) -> None:
    """Responds to user with a greeting."""
    user_name = message.from_user.full_name if message.from_user else "Пользователь"
    greeting = f"Привет, {hbold(user_name)}!"
    await message.answer(greeting)
