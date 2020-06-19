import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from application.clients.cts_client import CtsClient
from application.repositories.cts_repository import CtsRepository

from asynctest import CoroutineMock

from config import testconfig


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def cts_client():
    logger = Mock()
    config = testconfig
    client = CtsClient(logger, config)
    return client


@pytest.fixture(scope='function')
def cts_repository(cts_client):
    # cts_client, logger, scheduler, config
    logger = Mock()
    scheduler = Mock()
    config = testconfig

    repository = CtsRepository(cts_client, logger, scheduler, config)
    return repository
