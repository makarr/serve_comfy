import uuid

import httpx
from litestar import Controller, get, post, Response
from litestar.background_tasks import BackgroundTask
from litestar.exceptions.http_exceptions import NotFoundException

from src.config.constants import COMFY_URL
from .models import Text2VideoRequest, VideoResponse, VideoStatus
from .service import handle_t2v, get_status, load_mp4_bytes

class H3Controller(Controller):
    guards = []
    client = httpx.Client(base_url=COMFY_URL)

    @get("/status/{request_id:uuid}")
    async def check_status(self, request_id: uuid.UUID) -> VideoStatus:
        if status := get_status(self.client, request_id):
            return status
        raise NotFoundException

    @get("/result/{url_name:str}", media_type='video/mp4')
    async def serve_video(self, url_name: str) -> bytes:
        mp4_bytes = load_mp4_bytes(url_name)
        # case: not found
        if mp4_bytes is None:
            raise NotFoundException
        # case: found but can't load (0 bytes)
        # case: found and loaded successfully
        return mp4_bytes
    
    @post("/text2video")
    async def text2video(self, data: Text2VideoRequest) -> Response[VideoResponse]:
        request_id = uuid.uuid4()
        return Response(
            VideoResponse(request_id),
            background=BackgroundTask(
                handle_t2v,
                self.client,
                request_id,
                data
            )
        )