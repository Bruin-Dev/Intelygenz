import logging
from ssl import VerifyMode
from typing import Dict, List, Optional

import aiohttp
from application.config import insecure_http_proxies, secure_http_proxies
from application.scenario import Scenario, clear_current_scenario, get_current_scenario, set_current_scenario
from application.scenarios import bruin_webhook_scenarios, gateway_monitor_scenarios, rta_poll_scenarios
from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

log = logging.getLogger(__name__)

# Scenarios to be executed
scenarios: List[Scenario] = [
    *bruin_webhook_scenarios,
    *rta_poll_scenarios,
    *gateway_monitor_scenarios,
]

http = FastAPI()
HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


async def start(secure_proxies: Dict[int, Optional[str]], insecure_proxies: Dict[int, Optional[str]]):
    """
    Starts an hypercorn server that binds to any port declared in the proxies configuration.
    :param secure_proxies: secure proxies to be binded
    :param insecure_proxies: insecure proxies to be binded
    """
    config = Config()
    config.loglevel = "ERROR"
    config.use_reloader = True
    config.verify_mode = VerifyMode.CERT_NONE
    config.bind = [f"0.0.0.0:{port}" for port in secure_proxies.keys()]
    config.insecure_bind = [f"0.0.0.0:{port}" for port in insecure_proxies.keys()]
    config.certfile = "certs/server.crt"
    config.keyfile = "certs/server.key"

    log.info(f"HTTP server listening on ports {[port for port in insecure_proxies.keys()]}")
    log.info(f"HTTPS server listening on ports {[port for port in secure_proxies.keys()]}")
    log.info(f"To run the server scenarios run the following command: curl -X PUT http://localhost:8000/_run_scenarios")
    try:
        await serve(http, config)
    except Exception as e:
        log.error(e)


@http.put("/_run_scenarios", status_code=200)
async def _run_scenarios():
    """
    Endpoint to start running all the scenarios
    :return: the scenarios result
    """
    scenario_results = []
    for scenario in scenarios:
        set_current_scenario(scenario)
        log.info(f"===> [Scenario STARTED] {scenario.name}")
        scenario_result = await scenario.run()
        scenario_results.append(scenario_result)
        log.info(f"===> [Scenario {'PASSED' if scenario_result.passed else 'FAILED'}] {scenario.name}")
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
    secure_proxy = secure_http_proxies.get(request.url.port, None)
    insecure_proxy = insecure_http_proxies.get(request.url.port, None)
    proxied_address = secure_proxy or insecure_proxy
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
