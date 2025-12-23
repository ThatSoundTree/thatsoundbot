from io import BytesIO

from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1

from thatsoundbot.models import SpotifyTrack


def create_audio_file(track: SpotifyTrack, album_cover_data: bytes | None) -> BytesIO:
    """Create MP3 file with metadata and zero duration."""
    tags = ID3()

    tags.add(TIT2(encoding=3, text=track.name))
    tags.add(TPE1(encoding=3, text=", ".join(track.artists) if track.artists else "Unknown Artist"))

    if track.album:
        tags.add(TALB(encoding=3, text=track.album))

    if album_cover_data:
        tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=album_cover_data))

    output = BytesIO()
    tags.save(output, v2_version=3)
    output.seek(0)
    return output
