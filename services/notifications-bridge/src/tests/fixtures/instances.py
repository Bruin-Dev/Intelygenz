from unittest.mock import Mock

import aiohttp
import pytest

from application.actions.send_to_slack import SendToSlack
from application.clients.slack_client import SlackClient
from application.repositories.slack_repository import SlackRepository
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
async def slack_client() -> SlackClient:
    instance = SlackClient(config=testconfig.SLACK_CONFIG, session=Mock(spec_set=aiohttp.ClientSession))
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def slack_repository(slack_client) -> SlackRepository:
    instance = SlackRepository(slack_client=slack_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def send_to_slack_action(slack_repository) -> SendToSlack:
    instance = SendToSlack(slack_repository=slack_repository)
    wrap_all_methods(instance)

    return instance
