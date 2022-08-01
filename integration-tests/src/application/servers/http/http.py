import logging
from ssl import VerifyMode
from typing import Dict, List, Optional

import aiohttp
from application.config import http_proxies
from application.scenario import Scenario, clear_current_scenario, get_current_scenario, set_current_scenario
from application.scenarios import ExampleScenario
from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

log = logging.getLogger(__name__)

# Scenarios to be executed
scenarios: List[Scenario] = [ExampleScenario()]

http = FastAPI()
HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


async def start(proxies: Dict[int, Optional[str]]):
    """
    Starts an hypercorn server that binds to any port declared in the proxies configuration.
    :param proxies: proxies to be binded
    """
    log.info(f"Starting ASGI server on ports {[port for port in proxies.keys()]}...")

    config = Config()
    config.loglevel = "ERROR"
    config.use_reloader = True
    config.verify_mode = VerifyMode.CERT_NONE
    config.bind = [f"0.0.0.0:{port}" for port in proxies.keys()]

    log.info(f"ASGI server started on ports {[port for port in proxies.keys()]}")
    await serve(http, config)


@http.put("/_run_scenarios", status_code=200)
async def _run_scenarios():
    """
    Endpoint to start running all the scenarios
    :return: the scenarios result
    """
    scenario_results = []
    for scenario in scenarios:
        set_current_scenario(scenario)
        log.info(f"[Scenario] {scenario.name} started")
        scenario_result = await scenario.run()
        scenario_results.append(scenario_result)
        log.info(f"[Scenario] {scenario.name} {'passed' if scenario_result.passed else 'failed'}")
        clear_current_scenario()

    return scenario_results


@http.api_route("{path:path}", methods=HTTP_METHODS, status_code=200)
async def catch_all(request: Request):
    """
    Http requests capturing endpoint. The requests will be handled by the current scenario being executed.
    :return: a proxied or mocked response
    """
    log.debug(f"[{request.method}] {request.url.path}?{request.query_params} => {await request.body()}")
    response = await get_current_scenario().handle_asgi(request, resend)
    log.info(f"[{request.method}] {request.url.path}?{request.query_params} <= {response.body}")
    return response


async def resend(request: Request) -> Response:
    """
    The default behaviour for any path that was not handled in the scenario.
    The request will be resent to the proxied address if any.
    :param request: any request
    :return: a proxied or empty response
    """
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
