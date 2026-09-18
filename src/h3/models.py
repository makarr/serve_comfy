import uuid
from typing import Literal

from msgspec import Struct, UnsetType, UNSET

class Text2VideoRequest(Struct):
    prompt: str

class VideoResponse(Struct):
    request_id: uuid.UUID

class VideoStatus(Struct):
    request_id: uuid.UUID
    status: Literal[
        "processing",
        "error",
        "success"
    ]
    error_msg: str | UnsetType = UNSET
    video_url: str | UnsetType = UNSET