from litestar import Litestar

from src.h3.controller import H3Controller

app = Litestar(
    route_handlers=[H3Controller],
    debug=True
)