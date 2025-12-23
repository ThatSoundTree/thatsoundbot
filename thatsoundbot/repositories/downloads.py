import httpx

from thatsoundbot.models import SpotifyTrack
from thatsoundbot.settings import get_settings


async def create_download_task(track: SpotifyTrack, message_id: str | None) -> dict:
    """Create download task for track on external backend."""
    settings = get_settings()
    backend_url = f"{settings.DIRECT_API_URL}/api/v1/tasks"
    async with httpx.AsyncClient(timeout=30.0) as client:
        json_data = {
            "id": track.id,
            "name": track.name,
            "artists": track.artists,
            "album": track.album,
            "album_cover_url": track.album_cover_url,
            "download_url": track.external_urls,
            "duration_ms": track.duration_ms,
        }
        if message_id:
            json_data["message_id"] = message_id
        response = await client.post(backend_url, json=json_data)
        response.raise_for_status()
        return response.json() if response.content else {}
