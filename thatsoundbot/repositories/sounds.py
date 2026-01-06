from thatsoundbot.backend.client import APIClient
from thatsoundbot.core.models import RecentTracksResponse
from thatsoundbot.settings import get_settings


async def get_recent_tracks(hgramid: str) -> RecentTracksResponse:
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
