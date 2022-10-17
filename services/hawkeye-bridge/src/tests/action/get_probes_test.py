import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_probes import GetProbes


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


class TestGetProbesClient:
    def instance_test(self, hawkeye_repository):
        get_probes = GetProbes(hawkeye_repository)

        assert get_probes._hawkeye_repository is hawkeye_repository

    @pytest.mark.asyncio
    async def get_probes_ok_test(
        self, get_probes_init, default_call_with_params, response_get_probes_down_ok, any_msg, init_msg
    ):
        get_probes_init._hawkeye_repository.get_probes = AsyncMock(return_value=response_get_probes_down_ok)
        any_msg.data = to_json_bytes(default_call_with_params)
        await get_probes_init(any_msg)

        any_msg.respond.assert_awaited_once_with(data=json.dumps({**init_msg, **response_get_probes_down_ok}).encode())

    @pytest.mark.asyncio
    async def get_probes_no_filters_ok_test(
        self, get_probes_init, default_call_without_params, response_get_probes_down_ok, init_msg, any_msg
    ):
        get_probes_init._hawkeye_repository.get_probes = AsyncMock(return_value=response_get_probes_down_ok)
        any_msg.data = to_json_bytes(default_call_without_params)
        await get_probes_init(any_msg)

        any_msg.respond.assert_awaited_once_with(data=json.dumps({**init_msg, **response_get_probes_down_ok}).encode())

    @pytest.mark.asyncio
    async def get_probes_not_body_test(self, get_probes_init, default_call_without_body, response_not_body, any_msg):
        any_msg.data = to_json_bytes(default_call_without_body)
        await get_probes_init(any_msg)

        any_msg.respond.assert_awaited_once_with(data=json.dumps(response_not_body).encode())
