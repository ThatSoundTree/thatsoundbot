import io
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger
from mutagen.mp3 import MP3  # type: ignore[import-untyped]
from PIL import Image  # type: ignore[import-untyped]
from PIL.Image import Image as PILImage  # type: ignore[import-untyped]


async def get_thumbnail_from_mp3(mp3_path: Path) -> Optional[bytes]:
    """Extract album cover from MP3 file and optimize it for Telegram thumbnail. Returns optimized JPEG thumbnail (320x320px, <200KB, baseline JPEG) or None."""
    if not mp3_path.exists():
        return None

    audio_file = MP3(mp3_path)

    # Find APIC (album cover) tag
    if audio_file.tags is None:
        return None

    apic_keys = [key for key in audio_file.tags.keys() if key.startswith("APIC")]
    if not apic_keys:
        return None

    # Get first cover art
    apic = audio_file.tags[apic_keys[0]]
    cover_data = apic.data

    if not cover_data:
        return None

    # Optimize for Telegram
    optimized = _optimize_thumbnail(cover_data)

    # Verify it's valid JPEG
    if optimized and optimized.startswith(b'\xff\xd8'):
        return optimized
    return None


async def get_thumbnail_from_url(url: str) -> Optional[bytes]:
    """Download album cover from URL and optimize it for Telegram thumbnail. Returns optimized JPEG thumbnail (320x320px, <200KB, baseline JPEG) or None."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        image_data = response.content

        optimized = _optimize_thumbnail(image_data)

        # Verify it's valid JPEG
        if optimized and optimized.startswith(b'\xff\xd8'):
            return optimized
        return None


def _optimize_thumbnail(image_data: bytes, max_size: int = 320, quality: int = 85, max_file_size_kb: int = 200) -> bytes:
    """Optimize image for Telegram thumbnail. Args: image_data (raw image bytes), max_size (max width/height in pixels, default 320), quality (JPEG quality 1-100, default 85), max_file_size_kb (max file size in KB, default 200). Returns optimized baseline JPEG image bytes."""
    # Open image from bytes
    image: PILImage = Image.open(io.BytesIO(image_data))  # type: ignore[assignment]

    # Convert to RGB if necessary
    if image.mode in ("RGBA", "LA", "P"):
        rgb_image: PILImage = Image.new("RGB", image.size, (255, 255, 255))  # type: ignore[assignment]
        if image.mode == "P":
            image = image.convert("RGBA")  # type: ignore[assignment]
        rgb_image.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
        image = rgb_image  # type: ignore[assignment]
    elif image.mode != "RGB":
        image = image.convert("RGB")  # type: ignore[assignment]

    # Remove ICC profile to ensure sRGB
    if hasattr(image, 'info') and 'icc_profile' in image.info:
        image.info.pop('icc_profile', None)

    # Make image square (1:1 aspect ratio)
    width, height = image.size
    if width != height:
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        image = image.crop((left, top, right, bottom))  # type: ignore[assignment]

    # Resize if too large
    width, height = image.size
    if width > max_size or height > max_size:
        image = image.resize((max_size, max_size), Image.Resampling.LANCZOS)  # type: ignore[assignment]

    # Save as baseline JPEG, adjust quality to meet size requirement
    max_file_size_bytes = max_file_size_kb * 1024
    current_quality = quality

    for _ in range(5):
        output = io.BytesIO()
        image.save(
            output,
            format="JPEG",
            quality=current_quality,
            optimize=True,
            progressive=False,  # Baseline JPEG
        )
        optimized_data = output.getvalue()

        if len(optimized_data) <= max_file_size_bytes:
            break

        current_quality = max(50, current_quality - 10)

    if len(optimized_data) > max_file_size_bytes:
        logger.warning(
            "Thumbnail size {size_kb:.1f}KB exceeds Telegram limit of {max_kb}KB",
            size_kb=len(optimized_data) / 1024,
            max_kb=max_file_size_kb,
        )

    return optimized_data
