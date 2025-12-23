from io import BytesIO

from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1

from thatsoundbot.models import SpotifyTrack


_BASE_MP3_DATA = (
    b"\xff\xfb\x90\x00"
    + b"\x00" * 417
)

_base_mp3_buffer: BytesIO | None = None


def _get_base_mp3() -> BytesIO:
    """Get base MP3 file buffer with ID3 tags, creating it if needed."""
    global _base_mp3_buffer
    if _base_mp3_buffer is None:
        buffer = BytesIO(_BASE_MP3_DATA)
        tags = ID3()
        tags.save(buffer, v2_version=3)
        buffer.seek(0)
        _base_mp3_buffer = BytesIO(buffer.getvalue())
        _base_mp3_buffer.seek(0)
    return _base_mp3_buffer


async def create_audio_file(track: SpotifyTrack, album_cover_data: bytes | None) -> BytesIO:
    """Create MP3 file with metadata in memory using base template."""
    base_buffer = _get_base_mp3()
    base_buffer.seek(0)
    base_data = base_buffer.read()

    buffer = BytesIO(base_data)
    buffer.seek(0)

    tags = ID3(buffer)
    audio_start = buffer.tell()

    tags.delall("TIT2")
    tags.delall("TPE1")
    tags.delall("TALB")
    tags.delall("APIC")

    tags.add(TIT2(encoding=3, text=track.name))
    tags.add(TPE1(encoding=3, text=", ".join(track.artists) if track.artists else "Unknown Artist"))

    if track.album:
        tags.add(TALB(encoding=3, text=track.album))

    if album_cover_data:
        tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=album_cover_data))

    output = BytesIO()
    tags.save(output, v2_version=3)
    output.seek(0)
    id3_data = output.read()

    audio_data = base_data[audio_start:] if audio_start < len(base_data) else _BASE_MP3_DATA

    final_output = BytesIO()
    final_output.write(id3_data)
    final_output.write(audio_data)
    final_output.seek(0)
    return final_output
