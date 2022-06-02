import pytest
from application.actions.get_test_results import GetTestResults
from asynctest import CoroutineMock
from config import testconfig as config


class TestGetTestResults:
    def instance_test(self, logger, event_bus, hawkeye_repository):
        get_probes = GetTestResults(logger, config, event_bus, hawkeye_repository)

        assert get_probes._logger is logger
        assert get_probes._config is config
        assert get_probes._event_bus is event_bus
        assert get_probes._hawkeye_repository is hawkeye_repository

    @pytest.mark.asyncio
    async def get_test_result_ok_test(
        self, get_test_result_init, default_call_with_params_test_result, response_return_all_test, init_msg
    ):
        get_test_result_init._hawkeye_repository.get_test_results = CoroutineMock(return_value=response_return_all_test)
        get_test_result_init._event_bus.publish_message = CoroutineMock()
        await get_test_result_init.get_test_results(default_call_with_params_test_result)

        get_test_result_init._event_bus.publish_message.assert_awaited_once_with(
            "hawkeye.test.request", {**init_msg, **response_return_all_test}
        )

    @pytest.mark.asyncio
    async def get_test_no_ids_ok_test(self, get_test_result_init, default_call_without_params_test_result, init_msg):
        get_test_result_init._event_bus.publish_message = CoroutineMock()
        await get_test_result_init.get_test_results(default_call_without_params_test_result)

        get_test_result_init._event_bus.publish_message.assert_awaited_once_with(
            "hawkeye.test.request",
            {
                **init_msg,
                **{"request_id": "1234", "body": 'Must include "probe_uids" in the body of the request', "status": 400},
            },
        )

    @pytest.mark.asyncio
    async def get_test_no_body_ok_test(self, get_test_result_init, default_call_without_body_test_result, init_msg):
        get_test_result_init._event_bus.publish_message = CoroutineMock()
        await get_test_result_init.get_test_results(default_call_without_body_test_result)

        get_test_result_init._event_bus.publish_message.assert_awaited_once_with(
            "hawkeye.test.request",
            {**init_msg, **{"request_id": "1234", "body": 'Must include "body" in request', "status": 400}},
        )
