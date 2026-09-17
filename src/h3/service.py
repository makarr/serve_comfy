import uuid

from .database import insert_request, select_status
from .models import VideoStatus

def handle_t2v(request_id: uuid.UUID, prompt: str) -> None:
    insert_request(request_id)


def get_status(request_id: uuid.UUID) -> VideoStatus | None:
    if status := select_status(request_id):
        return VideoStatus(request_id, status)