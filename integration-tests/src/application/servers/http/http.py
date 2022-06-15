import logging
from ssl import VerifyMode
from typing import Dict, Optional

import aiohttp
from application.config import http_proxies
from application.scenario import clear_current_scenario, get_current_scenario, set_current_scenario
from application.scenarios import scenarios
from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

log = logging.getLogger(__name__)

http = FastAPI()
HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


# class HttpServer:
# proxies: Dict[int, Optional[str]]

# def __init__(self, proxies: Dict[int, Optional[str]]):
#     self.proxies = proxies


async def start(proxies: Dict[int, Optional[str]]):
    log.info(f"Starting ASGI server on ports {[port for port in proxies.keys()]}...")

    config = Config()
    config.loglevel = "ERROR"
    config.use_reloader = True
    config.verify_mode = VerifyMode.CERT_NONE
    config.bind = [f"0.0.0.0:{port}" for port in proxies.keys()]

    await serve(http, config)

    # logging.info("Shutting down")
    # for task in asyncio.Task.all_tasks():
    #     task.cancel()
    # logging.info("Bye")


@http.put("/run", status_code=200)
async def run():
    scenario_results = []
    for scenario in scenarios:
        set_current_scenario(scenario)
        log.info(f"[{scenario.name}] started")
        scenario_result = await scenario.run()
        scenario_results.append(scenario_result)
        log.info(f"[{scenario.name}] {'passed' if scenario_result.passed else 'failed'}")
        clear_current_scenario()

    return scenario_results


@http.api_route("{path:path}", methods=HTTP_METHODS, status_code=200)
async def catch_all(request: Request):
    log.info(f"[{request.method}] {request.url.path}")
    response = await get_current_scenario().handle_asgi(request, resend)
    log.info(f"[{request.method}] {request.url.path} => {response.body}")
    return response


async def resend(request: Request) -> Response:
    log.info(f"resend(request.path={request.url.path})")
    proxied_address = http_proxies.get(request.url.port, None)
    if not proxied_address:
        return JSONResponse({})

    proxied_url = f"{proxied_address}{request.url.path}"
    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=request.method,
            url=proxied_url,
            data=request.body(),
            params=request.query_params,
        )
        return Response(content=response.content, status_code=response.status, headers=response.headers)
