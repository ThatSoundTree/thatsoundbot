import asyncio
import tempfile
from pathlib import Path
from uuid import UUID

from aiogram.types import FSInputFile
from loguru import logger

from thatsoundbot.services.telegram import backup_track
from thatsoundbot.settings import get_tsapi_settings, get_tsripper_settings, TSAPISettings
from thatsoundbot.utils.http_client import HttpClient


async def scrobble_track(hgramid: str, track_id: str, track_provider: str) -> None | str | UUID:
    tsapi_settings = get_tsapi_settings()
    response = await HttpClient.get(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble",
        params={"track_id": track_id, "track_provider": track_provider},
        headers=tsapi_settings.get_header()
    )

    if response.status_code == 200:
        resp = response.json()
        return resp["tfile_url"]
    elif response.status_code != 503:
        logger.error(
            "[{hgramid}] [scrobble] [{track_id}] unexpected api error: {error_text}",
            hgramid=hgramid,
            track_id=track_id,
            error_text=response.text[:200],
        )
        return None

    resp = response.json()
    return UUID(resp["id"])


async def get_track_template(hgramid: str, scrobble_id: UUID, is_thumbnail_request: bool = False) -> tuple[bytes, str] | bool | None :
    tsripper = get_tsripper_settings()
    if is_thumbnail_request:
        url = tsripper.BASE_URL + f"/cache/{scrobble_id.hex}/thumbnail"
    else:
        url = tsripper.BASE_URL + f"/cache/{scrobble_id.hex}"

    response = await HttpClient.get(
        url=url,
    )

    if response.status_code == 204:
        return None
    elif response.status_code != 200:
        logger.error(
            "[{hgramid}] [ripper] [{scrobble_id}] unexpected api error: {error_text}",
            hgramid=hgramid,
            scrobble_id=scrobble_id.hex[:8],
            error_text=response.text[:200],
        )
        return False

    filename = response.headers["Content-Disposition"].split("filename=")[1]
    return response.content, filename


async def get_track_file(hgramid: str, scrobble_id: UUID) -> tuple[bytes, str] | bool | None :
    return await get_track_template(hgramid=hgramid, scrobble_id=scrobble_id)


async def get_track_thumbnail(hgramid: str, scrobble_id: UUID) -> tuple[bytes, str] | bool | None :
    return await get_track_template(hgramid=hgramid, scrobble_id=scrobble_id, is_thumbnail_request=True)


async def fetch_file_id_periodically(hgramid:str, scrobble_id: UUID) -> tuple[bytes, str] | None:
    tsripper_settings = get_tsripper_settings()
    while True:
        await asyncio.sleep(tsripper_settings.SCROBBLE_SLEEP_TIME)
        result = await get_track_file(hgramid=hgramid, scrobble_id=scrobble_id)
        if result is False:
            return None
        if isinstance(result, tuple):
            return result
        # result is None, continue waiting


def create_caption(track_id_with_provider: str) -> tuple[str, str]:
    track_id, provider_id_str = track_id_with_provider.split("!@#")
    provider_enum = TSAPISettings.Providers(int(provider_id_str))
    caption = f"{provider_enum.name}:{track_id}"
    return track_id, caption


def create_temp_files(file_in_bytes: bytes, thumbnail_in_bytes: bytes) -> tuple[Path, Path]:
    # Create temporary files
    _, audio_temp_path = tempfile.mkstemp(suffix='.mp3')
    audio_temp_file = Path(audio_temp_path)
    audio_temp_file.write_bytes(file_in_bytes)

    _, thumbnail_temp_path = tempfile.mkstemp(suffix='.jpg')
    thumbnail_temp_file = Path(thumbnail_temp_path)
    thumbnail_temp_file.write_bytes(thumbnail_in_bytes)
    return audio_temp_file, thumbnail_temp_file


async def process_backup_track(hgramid: str, scrobble_id: UUID, track_id_with_provider: str) -> str:
    tsapi_settings = get_tsapi_settings()

    file_result = await fetch_file_id_periodically(hgramid=hgramid, scrobble_id=scrobble_id)
    if not file_result:
        raise RuntimeError(f"Failed to fetch audio file for scrobble_id={scrobble_id}")
    file_in_bytes, filename = file_result

    thumbnail_result = await get_track_thumbnail(hgramid=hgramid, scrobble_id=scrobble_id)
    if not isinstance(thumbnail_result, tuple):
        raise RuntimeError(f"Failed to fetch thumbnail for scrobble_id={scrobble_id}")
    thumbnail_in_bytes, _ = thumbnail_result

    track_id, caption = create_caption(track_id_with_provider=track_id_with_provider)
    audio_temp_file, thumbnail_temp_file = create_temp_files(
        file_in_bytes=file_in_bytes, thumbnail_in_bytes=thumbnail_in_bytes
    )


    new_file_id = await backup_track(
        audio=FSInputFile(path=audio_temp_file, filename=filename),
        thumbnail=FSInputFile(path=thumbnail_temp_file, filename="thumbnail.jpg"),
        caption=caption
    )

    audio_temp_file.unlink(missing_ok=True)
    thumbnail_temp_file.unlink(missing_ok=True)

    response = await HttpClient.patch(
        url=tsapi_settings.BASE_URL + f"/{hgramid}/scrobble/",
        params={"external_track_id": track_id, "tfile_url": new_file_id},
        headers=tsapi_settings.get_header()
    )

    if response.status_code != 200:
        logger.error(
            "[{hgramid}] [scrobble] [caching] unexpected api error: {error_text}",
            hgramid=hgramid[:8],
            error_text=response.text[:200]
        )
        return new_file_id

    logger.info("[{hgramid}] [scrobble] [caching] success", hgramid=hgramid[:8])
    return new_file_id
