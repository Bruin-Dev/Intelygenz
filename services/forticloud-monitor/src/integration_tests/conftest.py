import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import pytest
from hypercorn import Config as HypercornConfig
from hypercorn.asyncio import serve
from nats.aio.client import Client
from quart import Quart, request
from redis.client import Redis

from app import Application, start
from config.config import Config

#
# Application setup
#


@pytest.fixture(scope="session")
def config():
    return Config(
        environment="local",
        environment_name="local",
        redis_host="localhost",
        nats_server="nats://localhost:4222",
        bruin_base_url="http://localhost:8001",
        bruin_login_url="http://localhost:8002",
        bruin_client_id="any_client_id",
        bruin_client_secret="any_client_secret",
        forticloud_base_url="http://localhost:8003",
        forticloud_account_id="any_account_id",
        forticloud_username="any_username",
        forticloud_password="any_password",
    )


@pytest.fixture(scope="session")
async def application(context, config, event_loop):
    application = Application()
    start(application, config, event_loop)
    yield application
    await application.close(stop_loop=False)


@pytest.hookimpl
def pytest_generate_tests(metafunc: pytest.Metafunc):
    if metafunc.definition.get_closest_marker("integration"):
        metafunc.fixturenames.append("application")


#
# Context setup
#


@pytest.fixture(scope="session")
async def context(docker_services, check_docker):
    docker_services.wait_until_responsive(timeout=5.0, pause=0.5, check=check_docker)


@pytest.fixture(scope="session")
async def check_docker(config):
    def inner():
        try:
            redis = Redis(host=config.redis_host, port=config.redis_port)
            redis.ping()
            redis.close()
            return True
        except:
            return False

    return inner


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(Path("src/integration_tests/docker-compose.yml").absolute())


@pytest.fixture(scope="session")
def docker_cleanup():
    return "kill"


#
# Clients setup
#


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope="session")
async def nats_client(application, config):
    nats_client = Client()
    await nats_client.connect([config.nats_server])
    yield nats_client
    await nats_client.close()


@pytest.fixture
async def bruin_server(event_loop):
    server = MockServer(["0.0.0.0:8001"])
    await server.start(loop=event_loop)
    yield server
    await server.close()


@pytest.fixture
async def bruin_login_server(event_loop):
    server = MockServer(["0.0.0.0:8002"])
    await server.start(loop=event_loop)
    yield server
    await server.close()


@pytest.fixture
async def forticloud_server(event_loop):
    server = MockServer(["0.0.0.0:8003"])
    await server.start(loop=event_loop)
    yield server
    await server.close()


@pytest.fixture
def bruin_login(bruin_login_server):
    async def builder(access_token: str = "any_access_token", expires_in: int = 3600):
        await bruin_login_server.mock_route(
            method="POST",
            path="/identity/connect/value",
            return_value=f'{{"access_token":"{access_token}","expires_in":{expires_in}}}',
        )

    return builder


@pytest.fixture
def forticloud_login(forticloud_server):
    async def builder(access_token: str = "any_access_token", expires_in: int = 3600):
        await forticloud_server.mock_route(
            method="POST",
            path="/auth",
            return_value=f'{{"access_token":"{access_token}","expires_in":{expires_in}}}',
        )

    return builder


class RouteMock:
    def __init__(self, path: str, return_value: str, method: str, content_type: str):
        self.path = path
        self.method = method
        self.return_value = return_value
        self.content_type = content_type
        self.reached = asyncio.Condition()

    async def was_reached(self, timeout: int) -> bool:
        async with self.reached:
            try:
                await asyncio.wait_for(self.reached.wait(), timeout)
                return True
            except:
                return False


@dataclass
class MockServer:
    bindings: List[str]
    routes: Dict[str, RouteMock] = field(default_factory=dict)
    server: Quart = field(init=False)
    _shutdown_signal: asyncio.Event = field(init=False, default_factory=asyncio.Event)
    _shutdown_completed: asyncio.Event = field(init=False, default_factory=asyncio.Event)

    def __post_init__(self):
        self.server = Quart("mock-server")
        self.server.add_url_rule("/<path:path>", view_func=self.handler, methods=["GET", "POST"])

    async def start(self, loop: AbstractEventLoop):
        hypercorn_config = HypercornConfig()
        hypercorn_config.bind = self.bindings
        coro = serve(self.server, hypercorn_config, shutdown_trigger=self._shutdown_signal.wait)
        task = loop.create_task(coro)
        task.add_done_callback(lambda _: self._shutdown_completed.set())

    async def handler(self, path: str):
        route = self.routes.get(f"/{path}")
        if not route:
            return "", 404
        elif request.method == route.method:
            async with route.reached:
                route.reached.notify_all()
            return route.return_value, 200, {"Content-type": route.content_type}

    async def mock_route(
        self, path: str, return_value: str, method: str = "GET", content_type: str = "application/json"
    ):
        route = RouteMock(path, return_value, method, content_type)
        self.routes[path] = route
        return route

    async def close(self):
        self._shutdown_signal.set()
        await self._shutdown_completed.wait()
