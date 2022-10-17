import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_test_results import GetTestResults


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


class TestGetTestResults:
    def instance_test(self, hawkeye_repository):
        get_probes = GetTestResults(hawkeye_repository)

        assert get_probes._hawkeye_repository is hawkeye_repository

    @pytest.mark.asyncio
    async def get_test_result_ok_test(
        self, get_test_result_init, default_call_with_params_test_result, response_return_all_test, init_msg, any_msg
    ):
        get_test_result_init._hawkeye_repository.get_test_results = AsyncMock(return_value=response_return_all_test)
        any_msg.data = to_json_bytes(default_call_with_params_test_result)
        await get_test_result_init(any_msg)

        any_msg.respond.assert_awaited_once_with(data=json.dumps({**init_msg, **response_return_all_test}).encode())

    @pytest.mark.asyncio
    async def get_test_no_ids_ok_test(
        self, get_test_result_init, default_call_without_params_test_result, init_msg, any_msg
    ):
        any_msg.data = to_json_bytes(default_call_without_params_test_result)
        await get_test_result_init(any_msg)

        any_msg.respond.assert_awaited_once_with(
            data=json.dumps(
                {
                    **init_msg,
                    **{
                        "request_id": "1234",
                        "body": 'Must include "probe_uids" in the body of the request',
                        "status": 400,
                    },
                }
            ).encode()
        )

    @pytest.mark.asyncio
    async def get_test_no_body_ok_test(
        self, get_test_result_init, default_call_without_body_test_result, init_msg, any_msg
    ):
        any_msg.data = to_json_bytes(default_call_without_body_test_result)
        await get_test_result_init(any_msg)

        any_msg.respond.assert_awaited_once_with(
            data=json.dumps(
                {**init_msg, **{"request_id": "1234", "body": 'Must include "body" in request', "status": 400}}
            ).encode()
        )
