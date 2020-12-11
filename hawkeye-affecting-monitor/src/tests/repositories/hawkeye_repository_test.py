from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from shortuuid import uuid

from application import nats_error_response
from application.repositories import hawkeye_repository as hawkeye_repository_module
from application.repositories.hawkeye_repository import HawkeyeRepository
from asynctest import CoroutineMock
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(hawkeye_repository_module, 'uuid', return_value=uuid_)


class TestHawkeyeRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        assert hawkeye_repository._event_bus is event_bus
        assert hawkeye_repository._logger is logger
        assert hawkeye_repository._config is config
        assert hawkeye_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_tests_results_ok_test(self):
        probe_uid = "b8:27:eb:76:a8:de"
        probe_uids = [
            probe_uid,
        ]

        interval = {
            'start': '2020-12-24 10:00:00',
            'end': '2020-12-24 11:00:00',
        }

        request = {
            'request_id': uuid_,
            'body': {
                'probe_uids': probe_uids,
                'interval': interval,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                probe_uid: [
                    {
                        "summary": {
                            "id": "2952796",
                            "date": "2020-12-11T12:01:32Z",
                            "duration": "30",
                            "status": "Failed",
                            "reasonCause": "",
                            "tdrId": "2952796",
                            "identifier": "Core",
                            "module": "MESH",
                            "testId": "335",
                            "testType": "Network KPI",
                            "parameters": " DSCP Setting: Best Effort",
                            "probeFrom": "Vi_Pi_DRI test",
                            "probeTo": "V_Basement",
                            "mesh": 1,
                            "testOptions": "DSCP Setting: Best Effort ",
                            "meshId": "CORE"
                        },
                        "metrics": [
                            {
                                "metric": "Jitter (ms)",
                                "pairName": "KPI from->to",
                                "value": "6",
                                "threshold": "5",
                                "thresholdType": "0",
                                "status": "Failed"
                            },
                            {
                                "metric": "Loss",
                                "pairName": "KPI from->to",
                                "value": "0",
                                "threshold": "0.2",
                                "thresholdType": "0",
                                "status": "Passed"
                            },
                        ],
                    },
                ],
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_tests_results_with_rpc_request_failing_test(self):
        probe_uid = "b8:27:eb:76:a8:de"
        probe_uids = [
            probe_uid,
        ]

        interval = {
            'start': '2020-12-24 10:00:00',
            'end': '2020-12-24 11:00:00',
        }

        request = {
            'request_id': uuid_,
            'body': {
                'probe_uids': probe_uids,
                'interval': interval,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tests_results_with_rpc_request_returning_non_2xx_status_test(self):
        probe_uid = "b8:27:eb:76:a8:de"
        probe_uids = [
            probe_uid,
        ]

        interval = {
            'start': '2020-12-24 10:00:00',
            'end': '2020-12-24 11:00:00',
        }

        request = {
            'request_id': uuid_,
            'body': {
                'probe_uids': probe_uids,
                'interval': interval,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Hawkeye',
            'status': 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_tests_results(probe_uids=probe_uids, interval=interval)

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.test.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_tests_results_for_affecting_monitoring_test(self):
        probe_1_uid = "b8:27:eb:76:a8:de"
        probe_2_uid = "c8:27:fc:76:b8:ef"
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
        ]

        tests_results_response = {
            'request_id': uuid_,
            'body': {
                probe_1_uid: [
                    {
                        "summary": {
                            "id": "2952796",
                            "date": "2020-12-11T12:01:32Z",
                            "duration": "30",
                            "status": "Failed",
                            "reasonCause": "",
                            "tdrId": "2952796",
                            "identifier": "Core",
                            "module": "MESH",
                            "testId": "335",
                            "testType": "Network KPI",
                            "parameters": " DSCP Setting: Best Effort",
                            "probeFrom": "Vi_Pi_DRI test",
                            "probeTo": "V_Basement",
                            "mesh": 1,
                            "testOptions": "DSCP Setting: Best Effort ",
                            "meshId": "CORE"
                        },
                        "metrics": [
                            {
                                "metric": "Jitter (ms)",
                                "pairName": "KPI from->to",
                                "value": "6",
                                "threshold": "5",
                                "thresholdType": "0",
                                "status": "Failed"
                            },
                            {
                                "metric": "Loss",
                                "pairName": "KPI from->to",
                                "value": "0",
                                "threshold": "0.2",
                                "thresholdType": "0",
                                "status": "Passed"
                            },
                        ],
                    },
                ],
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)
        hawkeye_repository.get_tests_results = CoroutineMock(return_value=tests_results_response)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(hawkeye_repository_module, 'datetime', new=datetime_mock):
            result = await hawkeye_repository.get_tests_results_for_affecting_monitoring(probe_uids=probe_uids)

        scan_interval = {
            'start': current_datetime - timedelta(seconds=config.MONITOR_CONFIG['scan_interval']),
            'end': current_datetime,
        }
        hawkeye_repository.get_tests_results.assert_awaited_once_with(probe_uids=probe_uids, interval=scan_interval)
        assert result == tests_results_response
