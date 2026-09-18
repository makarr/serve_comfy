import uuid

from msgspec import Struct, UnsetType, UNSET

class Text2VideoRequest(Struct):
    prompt: str

class VideoResponse(Struct):
    request_id: uuid.UUID

class VideoStatus(Struct):
    request_id: uuid.UUID
    status: str
    error_msg: str | UnsetType = UNSET
    video_url: str | UnsetType = UNSET