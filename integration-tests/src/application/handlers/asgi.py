import logging

from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)


async def resend_request(request: Request) -> Response:
    try:
        json = await request.json()
    except Exception as e:
        json = None
        log.warning(e)

    log.info(f"Proxying {request.url.port}:{request.url.path}, json={json}")
    return Response(content={}, status_code=200)
