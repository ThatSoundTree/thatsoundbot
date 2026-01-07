from typing import List, Optional

from pydantic import BaseModel, Field


class SpotifyTrack(BaseModel):
    """Spotify track model for recently played tracks."""

    id: str = Field(..., description="Spotify track ID")
    name: str = Field(..., description="Track name")
    artists: List[str] = Field(..., description="List of artist names")
    album: Optional[str] = Field(default=None, description="Album name")
    album_cover_url: Optional[str] = Field(default=None, description="Album cover image URL")
    external_urls: Optional[str] = Field(default=None, description="Spotify track URL")
    duration_ms: Optional[int] = Field(default=None, description="Track duration in milliseconds")


class RecentTracksResponse(BaseModel):
    """Response model for recently played tracks."""

    tracks: List[SpotifyTrack] = Field(..., description="List of recently played tracks")
