from thatsoundbot.backend.client import APIClient
from thatsoundbot.models import RecentTracksResponse, User
from thatsoundbot.settings import get_settings


async def get_recent_tracks(htelegram_id: str) -> RecentTracksResponse:
    """Get recently played tracks for user."""
    settings = get_settings()
    async with APIClient(settings) as client:
        response = await client.get(f"/api/v1/sounds/recent-tracks/{htelegram_id}")

        if "data" in response:
            tracks_data = response["data"]
        else:
            tracks_data = response

        if not isinstance(tracks_data, dict):
            tracks_data = {}

        return RecentTracksResponse.model_validate(tracks_data)


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
