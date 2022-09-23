import asyncio
from pathlib import Path

import pytest

from app import Application, start
from config.config import Config


@pytest.fixture(scope="package")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope="package")
def config():
    return Config()


@pytest.fixture(scope="package")
async def application(docker_services, config, event_loop):
    application = Application()
    start(application, config, event_loop)
    yield application
    await application.close()


@pytest.hookimpl
def pytest_generate_tests(metafunc: pytest.Metafunc):
    if metafunc.definition.get_closest_marker("integration"):
        metafunc.fixturenames.append("application")


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(Path("src/integration_tests/docker-compose.yml").absolute())


@pytest.fixture(scope="session")
def docker_cleanup():
    return "kill"
