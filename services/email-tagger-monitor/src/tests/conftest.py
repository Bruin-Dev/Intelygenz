import json
from typing import Any, Callable
from unittest.mock import Mock, create_autospec

import pytest
from framework.nats.client import Client
from nats.aio.msg import Msg

from application.repositories.storage_repository import StorageRepository
from application.server.api_server import APIServer
from config import testconfig as config

# Scopes
# - function
# - module
# - session


@pytest.fixture(scope="function")
def logger():
    return Mock()


@pytest.fixture(scope="function")
def redis():
    return Mock()


@pytest.fixture(scope="function")
def bruin_repository():
    return Mock()


@pytest.fixture(scope="function")
def new_emails_repository():
    return Mock()


@pytest.fixture(scope="function")
def new_tickets_repository():
    return Mock()


@pytest.fixture(scope="function")
def notifications_repository():
    return Mock()


@pytest.fixture(scope="function")
def utils_repository():
    return Mock()


@pytest.fixture(scope="function")
def api_server_test(
    new_emails_repository,
    bruin_repository,
    new_tickets_repository,
    notifications_repository,
    utils_repository,
):
    return APIServer(
        config,
        new_emails_repository,
        new_tickets_repository,
        notifications_repository,
        utils_repository,
    )


@pytest.fixture(scope="function")
def storage_repository(redis):
    return StorageRepository(config, redis)


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(Client)


@pytest.fixture
def make_msg(event_bus: Client) -> Callable[[Any], Msg]:
    def builder(data: Any) -> Msg:
        return Msg(_client=event_bus, data=json.dumps(data).encode())

    return builder
