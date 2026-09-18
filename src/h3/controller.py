import uuid

import httpx
from litestar import Controller, get, post, Response
from litestar.background_tasks import BackgroundTask
from litestar.exceptions.http_exceptions import NotFoundException

from src.config.constants import COMFY_URL
from .models import Text2VideoRequest, VideoResponse, VideoStatus
from .service import handle_t2v, get_status

class H3Controller(Controller):
    guards = []
    client = httpx.Client(base_url=COMFY_URL)

    @get("/status/{request_id:uuid}")
    async def check_status(self, request_id: uuid.UUID) -> VideoStatus:
        if status := get_status(request_id):
            return status
        raise NotFoundException
    
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