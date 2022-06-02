import pytest
from application.actions.get_probes import GetProbes
from asynctest import CoroutineMock
from config import testconfig as config


class TestGetProbesClient:
    def instance_test(self, logger, event_bus, hawkeye_repository):
        get_probes = GetProbes(logger, config, event_bus, hawkeye_repository)

        assert get_probes._logger is logger
        assert get_probes._config is config
        assert get_probes._event_bus is event_bus
        assert get_probes._hawkeye_repository is hawkeye_repository

    @pytest.mark.asyncio
    async def get_probes_ok_test(
        self, get_probes_init, default_call_with_params, response_get_probes_down_ok, init_msg
    ):
        get_probes_init._hawkeye_repository.get_probes = CoroutineMock(return_value=response_get_probes_down_ok)
        get_probes_init._event_bus.publish_message = CoroutineMock()
        await get_probes_init.get_probes(default_call_with_params)

        get_probes_init._event_bus.publish_message.assert_awaited_once_with(
            "hawkeye.probe.request", {**init_msg, **response_get_probes_down_ok}
        )

    @pytest.mark.asyncio
    async def get_probes_no_filters_ok_test(
        self, get_probes_init, default_call_without_params, response_get_probes_down_ok, init_msg
    ):
        get_probes_init._hawkeye_repository.get_probes = CoroutineMock(return_value=response_get_probes_down_ok)
        get_probes_init._event_bus.publish_message = CoroutineMock()
        await get_probes_init.get_probes(default_call_without_params)

        get_probes_init._event_bus.publish_message.assert_awaited_once_with(
            "hawkeye.probe.request", {**init_msg, **response_get_probes_down_ok}
        )

    @pytest.mark.asyncio
    async def get_probes_not_body_test(self, get_probes_init, default_call_without_body, response_not_body):
        get_probes_init._event_bus.publish_message = CoroutineMock()
        await get_probes_init.get_probes(default_call_without_body)

        get_probes_init._event_bus.publish_message.assert_awaited_once_with("hawkeye.probe.request", response_not_body)
