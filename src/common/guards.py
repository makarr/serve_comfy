from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from litestar.exceptions import NotAuthorizedException

from config.constants import API_KEY

async def api_key_guard(
    connection: ASGIConnection,
    _: BaseRouteHandler
    ) -> None:    
    try:
        api_key = connection.headers.get(
            "Authorization"
        ).split()[1]
        if api_key != API_KEY:
            raise NotAuthorizedException("Invalid API key")
    except:
        raise NotAuthorizedException("Invalid API key")