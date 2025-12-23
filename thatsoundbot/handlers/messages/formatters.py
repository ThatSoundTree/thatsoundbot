from thatsoundbot.models import SpotifyTrack


def format_artists(artists: list[str]) -> str:
    """Format artists list as string."""
    return ", ".join(artists) if artists else "Unknown Artist"


def format_track_text(track: SpotifyTrack) -> str:
    """Format track data as message text."""
    artists = format_artists(track.artists)
    text = f"🎵 <b>{track.name}</b>\n👤 {artists}"

    if track.album:
        text += f"\n💿 {track.album}"

    if track.duration_ms:
        duration_sec = track.duration_ms // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        text += f"\n⏱ {minutes}:{seconds:02d}"

    if track.external_urls:
        text += f"\n🔗 <a href='{track.external_urls}'>Open in Spotify</a>"

    return text
