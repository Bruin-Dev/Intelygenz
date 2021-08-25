from unittest.mock import Mock
import pytest

from application.server.api_server import APIServer
from application.repositories.storage_repository import StorageRepository
from config import testconfig as config


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def redis():
    return Mock()


@pytest.fixture(scope='function')
def bruin_repository():
    return Mock()


@pytest.fixture(scope='function')
def repair_tickets_repository():
    return Mock()


@pytest.fixture(scope='function')
def repair_tickets_kre_repository():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository():
    return Mock()


@pytest.fixture(scope='function')
def utils_repository():
    return Mock()


@pytest.fixture(scope='function')
def storage_repository(logger, redis):
    return StorageRepository(config, logger, redis)
