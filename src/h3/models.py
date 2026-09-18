import uuid
from typing import Literal

from msgspec import Struct, UnsetType, UNSET

class Text2VideoRequest(Struct):
    prompt: str
    num_seconds: float = 5.
    aspect_ratio: Literal[
        "9:16",
        "3:4",
        "1:1",
        "4:3",
        "16:9",
        "21:9"
    ] = "16:9"
    resolution: Literal["768p"] = "768p"
    prompt_expansion: Literal[
        "detailed",
        "balanced",
        "none",
        "auto"
    ] = "auto"
    audio: bool = True

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