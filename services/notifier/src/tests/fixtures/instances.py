from unittest.mock import Mock

import pytest
from application.actions.send_to_slack import SendToSlack
from application.clients.slack_client import SlackClient
from application.repositories.slack_repository import SlackRepository
from asynctest import create_autospec
from config import testconfig
from igz.packages.eventbus.eventbus import EventBus
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger():
    # Let's suppress all logs in tests
    return Mock()


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope="function")
def slack_client(logger) -> SlackClient:
    instance = SlackClient(logger=logger, config=testconfig.SLACK_CONFIG)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def slack_repository(logger, slack_client) -> SlackRepository:
    instance = SlackRepository(logger=logger, config=testconfig, slack_client=slack_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def send_to_slack_action(logger, slack_repository, event_bus) -> SendToSlack:
    instance = SendToSlack(logger=logger, config=testconfig, slack_repository=slack_repository, event_bus=event_bus)
    wrap_all_methods(instance)

    return instance
