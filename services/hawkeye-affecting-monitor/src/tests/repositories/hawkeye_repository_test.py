from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application import nats_error_response
from application.repositories import hawkeye_repository as hawkeye_repository_module
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(hawkeye_repository_module, "uuid", return_value=uuid_)


class TestHawkeyeRepository:
    def instance_test(self, hawkeye_repository, event_bus, logger, notifications_repository):
        assert hawkeye_repository._event_bus is event_bus
        assert hawkeye_repository._logger is logger
        assert hawkeye_repository._config is testconfig
        assert hawkeye_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_tests_results_ok_test(self, hawkeye_repository, probe_1_uid, passed_icmp_test_result_1_on_2020_01_16):
        probe_uids = [
            probe_1_uid,
        ]

        interval = {
            "start": "2020-12-24 10:00:00",
            "end": "2020-12-24 11:00:00",
        }

        request = {
            "request_id": uuid_,
            "body": {
                "probe_uids": probe_uids,
                "interval": interval,
            },
        }
        response = {
            "request_id": uuid_,
            "body": {
                probe_1_uid: [
                    passed_icmp_test_result_1_on_2020_01_16,
                ],
            },
            "status": 200,
        }

        hawkeye_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_tests_results_with_rpc_request_failing_test(self, hawkeye_repository, probe_1_uid):
        probe_uids = [
            probe_1_uid,
        ]

        interval = {
            "start": "2020-12-24 10:00:00",
            "end": "2020-12-24 11:00:00",
        }

        request = {
            "request_id": uuid_,
            "body": {
                "probe_uids": probe_uids,
                "interval": interval,
            },
        }

        hawkeye_repository._event_bus.rpc_request.side_effect = Exception
        hawkeye_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        hawkeye_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tests_results_with_rpc_request_returning_non_2xx_status_test(
        self, hawkeye_repository, probe_1_uid, hawkeye_500_response
    ):
        probe_uids = [
            probe_1_uid,
        ]

        interval = {
            "start": "2020-12-24 10:00:00",
            "end": "2020-12-24 11:00:00",
        }

        request = {
            "request_id": uuid_,
            "body": {
                "probe_uids": probe_uids,
                "interval": interval,
            },
        }

        hawkeye_repository._event_bus.rpc_request.return_value = hawkeye_500_response
        hawkeye_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        hawkeye_repository._logger.error.assert_called()
        assert result == hawkeye_500_response

    @pytest.mark.asyncio
    async def get_tests_results_for_affecting_monitoring_test(
        self, hawkeye_repository, probe_1_uid, probe_2_uid, passed_icmp_test_result_1_on_2020_01_16
    ):
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
        ]

        tests_results_response = {
            "request_id": uuid_,
            "body": {
                probe_1_uid: [
                    passed_icmp_test_result_1_on_2020_01_16,
                ],
            },
            "status": 200,
        }

        hawkeye_repository.get_tests_results.return_value = tests_results_response

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(hawkeye_repository_module, "datetime", new=datetime_mock):
            result = await hawkeye_repository.get_tests_results_for_affecting_monitoring(probe_uids=probe_uids)

        scan_interval = {
            "start": current_datetime - timedelta(seconds=testconfig.MONITOR_CONFIG["scan_interval"]),
            "end": current_datetime,
        }
        hawkeye_repository.get_tests_results.assert_awaited_once_with(probe_uids=probe_uids, interval=scan_interval)
        assert result == tests_results_response
