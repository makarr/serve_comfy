from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from src.h3.controller import H3Controller, serve_video

app = Litestar(
    route_handlers=[H3Controller, serve_video],
    openapi_config=OpenAPIConfig(title="h3", version="0.1"),
    debug=True
)