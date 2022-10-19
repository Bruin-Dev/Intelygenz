from datetime import timedelta
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from bruin_client import BruinClient, BruinResponse

from application.repositories import BruinRepository, TaskSettings


@pytest.fixture
def any_bruin_repository(any_bruin_response):
    def builder(send: AsyncMock = AsyncMock(return_value=any_bruin_response)):
        bruin_client = Mock(BruinClient)
        bruin_client.send = send

        task_settings = TaskSettings(auto_resolution_grace_period=timedelta(hours=1), max_auto_resolutions=1)

        return BruinRepository(bruin_client, task_settings)

    return builder


@pytest.fixture
def any_bruin_response():
    return BruinResponse(status=HTTPStatus.OK, text="{}")
