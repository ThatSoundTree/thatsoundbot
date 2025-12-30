def get_filename_from_task_data(task_data: dict, task_id: str) -> str:
    """Get filename from task data."""
    track_artists = task_data.get("track_artists", "")
    track_name = task_data.get("track_name", "")
    return f"{track_artists} - {track_name}.mp3" if track_artists and track_name else f"{task_id}.mp3"
