import uuid

from msgspec import Struct

class Text2VideoRequest(Struct):
    prompt: str

class VideoResponse(Struct):
    request_id: uuid.UUID

class VideoStatus(Struct):
    request_id: uuid.UUID
    status: str