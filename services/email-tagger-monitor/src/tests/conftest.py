from unittest.mock import Mock

import pytest
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
    logger, new_emails_repository, bruin_repository, new_tickets_repository, notifications_repository, utils_repository
):
    return APIServer(
        logger, config, new_emails_repository, new_tickets_repository, notifications_repository, utils_repository
    )


@pytest.fixture(scope="function")
def storage_repository(logger, redis):
    return StorageRepository(config, logger, redis)
