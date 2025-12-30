from thatsoundbot.backend.client import APIClient
from thatsoundbot.models import User
from thatsoundbot.settings import get_settings


async def mention_user(htelegram_id: str) -> User:
    """Get or create a user by hashed Telegram ID."""
    settings = get_settings()
    async with APIClient(settings) as client:
        response = await client.post(f"/api/v1/users/{htelegram_id}")

        if "data" in response:
            user_data = response["data"]
        else:
            user_data = response

        if not isinstance(user_data, dict):
            user_data = {}

        if "message" in response:
            user_data["message"] = response["message"]

        user = User.model_validate(user_data)
        return user
