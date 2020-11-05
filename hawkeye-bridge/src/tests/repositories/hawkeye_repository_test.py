from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock

from application.repositories.hawkeye_repository import HawkeyeRepository
from config import testconfig as config


class TestHawkeyeRepository:
    def instance_test(self, hawkeye_client):
        logger = Mock()

        hawkeye_repository = HawkeyeRepository(logger, hawkeye_client, config)

        assert hawkeye_repository._logger is logger
        assert hawkeye_repository._hawkeye_client is hawkeye_client
        assert hawkeye_repository._config is config

    @pytest.mark.asyncio
    async def get_probes_ok_test(self, hawkeye_repository, default_call_with_params, response_get_probes_down_ok):
        hawkeye_repository._hawkeye_client.get_probes = CoroutineMock(side_effect=[response_get_probes_down_ok])
        result = await hawkeye_repository.get_probes(default_call_with_params)
        assert len(result['body']) == 2
        assert result['status'] == 200

    @pytest.mark.asyncio
    async def get_probes_big_ok_test(self, hawkeye_repository, default_call_with_params,
                                     first_response_get_probes_down_big_ok, second_response_get_probes_down_big_ok,
                                     third_response_get_probes_down_big_ok):
        hawkeye_repository._hawkeye_client.get_probes = CoroutineMock(
            side_effect=[first_response_get_probes_down_big_ok, second_response_get_probes_down_big_ok,
                         third_response_get_probes_down_big_ok])
        result = await hawkeye_repository.get_probes(default_call_with_params)
        assert len(result['body']) == 1024
        assert result['status'] == 200

    @pytest.mark.asyncio
    async def get_probes_ko_test(self, hawkeye_repository, default_call_with_params, response_bad_status):
        hawkeye_repository._hawkeye_client.get_probes = CoroutineMock(return_value=response_bad_status)
        result = await hawkeye_repository.get_probes(default_call_with_params)
        assert result['body'] == []
        assert result['status'] == 200

    @pytest.mark.asyncio
    async def get_probes_check_retries_test(self, hawkeye_repository, default_call_with_params,
                                            response_get_probes_down_not_end_ok, response_bad_status):
        hawkeye_repository._hawkeye_client.get_probes = CoroutineMock(
            side_effect=[response_get_probes_down_not_end_ok, response_bad_status, response_bad_status,
                         response_bad_status, response_bad_status, response_bad_status, response_bad_status])
        result = await hawkeye_repository.get_probes(default_call_with_params)
        hawkeye_repository._logger.error.assert_called_once()
        assert result['body'] == response_get_probes_down_not_end_ok['body']['records']
        assert result['status'] == 200

    @pytest.mark.asyncio
    async def get_probes_check_retries_2_test(self, hawkeye_repository, default_call_with_params,
                                              response_get_probes_down_ok, response_bad_status,
                                              response_get_probes_down_not_end_ok):
        hawkeye_repository._hawkeye_client.get_probes = CoroutineMock(
            side_effect=[response_get_probes_down_not_end_ok, response_bad_status, response_bad_status,
                         response_get_probes_down_ok])
        result = await hawkeye_repository.get_probes(default_call_with_params)
        assert result['body'] == response_get_probes_down_ok['body']['records'] * 2
        assert result['status'] == 200
