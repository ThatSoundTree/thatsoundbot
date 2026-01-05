import asyncio
from pathlib import Path
from tempfile import gettempdir

from loguru import logger

from thatsoundbot.utils.http_client2 import TSDirectHTTPClient


async def wait_for_task_ready(
    status_url: str, task_id: str, htelegram_id_short: str, check_interval: int
) -> dict:
    """Wait until task is ready and return task data."""
    while True:
        await asyncio.sleep(check_interval)
        response = await TSDirectHTTPClient.get(status_url)

        if response.status_code == 404:
            continue

        if response.status_code != 200:
            logger.warning(
                "Unexpected status code when checking task: task_id={task_id}, "
                "htelegram_id={htelegram_id_short}, status={status}",
                task_id=task_id,
                htelegram_id_short=htelegram_id_short,
                status=response.status_code,
            )
            continue

        task_data = response.json()
        if task_data.get("status") == "uploaded":
            return task_data


async def download_task_file(download_url: str, task_id: str) -> Path:
    """Download file and return path."""
    file_response = await TSDirectHTTPClient.get(download_url)
    file_response.raise_for_status()

    file_path = Path(gettempdir()) / f"{task_id}.mp3"
    with open(file_path, "wb") as f:
        async for chunk in file_response.aiter_bytes():
            f.write(chunk)

    return file_path
