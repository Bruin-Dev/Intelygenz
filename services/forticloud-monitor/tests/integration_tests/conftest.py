import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import pytest
from nats.aio.client import Client
from redis.client import Redis
from sanic import HTTPResponse, Request, Sanic
from sanic.server import AsyncioServer

from app import Application, Settings, start


@pytest.fixture(scope="module")
def settings():
    return Settings(
        environment="local",
        environment_name="local",
        redis_host="localhost",
        nats_servers=["nats://localhost:4222"],
        bruin_base_url="http://localhost:8001",
    )


@pytest.fixture(scope="module")
async def bruin_server(event_loop):
    mock_server = MockServer("bruin_mock_server", port=8001)
    await mock_server.start(loop=event_loop)
    yield mock_server
    mock_server.close()


@pytest.fixture(scope="module")
async def application(docker, settings, event_loop):
    application = Application()
    await start(application, settings, event_loop)
    yield application
    await application.close()


@pytest.fixture(scope="module")
async def nats_client(application, settings):
    nats_client = Client()
    await nats_client.connect(settings.nats_servers)
    yield nats_client
    await nats_client.close()


@pytest.fixture(scope="module")
async def docker(docker_services, settings):
    def check_services():
        try:
            redis = Redis(host=settings.redis_host, port=settings.redis_port)
            redis.ping()
            redis.close()
            return True
        except:
            return False

    docker_services.wait_until_responsive(timeout=5.0, pause=0.5, check=check_services)


@pytest.hookimpl
def pytest_generate_tests(metafunc: pytest.Metafunc):
    if metafunc.definition.get_closest_marker("integration"):
        metafunc.fixturenames.append("application")


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(Path("tests/integration_tests/docker-compose.yml").absolute())


@pytest.fixture(scope="session")
def docker_cleanup():
    return "kill"


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.new_event_loop()


class RouteMock:
    def __init__(self, path: str, return_value: str, method: str):
        self.path = path
        self.method = method
        self.return_value = return_value
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
    name: str
    port: int
    routes: Dict[str, RouteMock] = field(default_factory=dict)
    server: AsyncioServer = field(init=False)
    sanic: Sanic = field(init=False)

    async def handler(self, request: Request, **kwargs):
        route = self.routes.get(request.path)
        if not route:
            return HTTPResponse(status=404)
        elif request.method == route.method:
            async with route.reached:
                route.reached.notify_all()
            return HTTPResponse(body=route.return_value)

    async def mock_route(self, path: str, return_value: str, method: str = "GET"):
        route = RouteMock(path, return_value, method)
        self.routes[path] = route
        return route

    async def start(self, loop: AbstractEventLoop):
        self.sanic = Sanic(self.name)
        self.sanic.add_route(self.handler, "/<path:path>", methods=["GET", "POST"])
        self.server = await self.sanic.create_server(port=self.port, return_asyncio_server=True)
        await self.server.startup()
        loop.create_task(self.server.start_serving())

    def close(self):
        self.server.close()
        self.sanic.stop()


# @pytest.mark.integration
# @pytest.fixture(scope="session")
# def integration_test(docker_services: Services):
#     pass
