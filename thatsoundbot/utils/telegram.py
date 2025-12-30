from aiogram.types import Message


def extract_file_id(sent_message: Message) -> str | None:
    """Extract file_id from sent message."""
    return (
        sent_message.audio.file_id
        if sent_message.audio
        else sent_message.document.file_id
        if sent_message.document
        else sent_message.voice.file_id
        if sent_message.voice
        else None
    )
