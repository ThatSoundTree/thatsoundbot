from thatsoundbot.backend.client import APIClient
from thatsoundbot.models import User
from thatsoundbot.settings import get_settings


async def mention_user(htelegram_id: str) -> User:
    """Get or create a user by hashed Telegram ID."""
    settings = get_settings()
    async with APIClient(settings) as client:
        response = await client.post(f"/api/v1/users/{htelegram_id}")

        # Extract user data from response wrapper
        if isinstance(response, dict):
            user_data = response.get("data", {})
            if not isinstance(user_data, dict):
                user_data = {}
            # Extract message from top-level response if it exists
            if "message" in response:
                user_data["message"] = response["message"]
        else:
            # If response is not a dict, treat it as user data directly
            user_data = response if isinstance(response, dict) else {}

        user = User.model_validate(user_data)
        return user
