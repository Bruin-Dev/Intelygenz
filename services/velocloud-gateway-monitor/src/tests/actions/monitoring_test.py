from datetime import datetime
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from application.actions import monitoring as monitoring_module
from application.actions.monitoring import GatewayPair
from application.dataclasses import Gateway, GatewayList
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(monitoring_module, "uuid", return_value=uuid_)


class TestMonitor:
    def instance_test(
        self,
        monitor,
        event_bus,
        scheduler,
        servicenow_repository,
        velocloud_repository,
        notifications_repository,
    ):

        assert monitor._event_bus is event_bus
        assert monitor._scheduler is scheduler
        assert monitor._config is testconfig
        assert monitor._velocloud_repository is velocloud_repository
        assert monitor._servicenow_repository is servicenow_repository
        assert monitor._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def start_monitoring_with_exec_on_start_test(self, monitor):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(monitoring_module, "datetime", new=datetime_mock):
            with patch.object(monitoring_module, "timezone", new=Mock()):
                await monitor.start_monitoring(exec_on_start=True)

        monitor._scheduler.add_job.assert_called_once_with(
            monitor._monitoring_process,
            "interval",
            seconds=monitor._config.MONITOR_CONFIG["monitoring_job_interval"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_monitor_process",
        )

    @pytest.mark.asyncio
    async def start_monitoring_with_no_exec_on_start_test(self, monitor):
        await monitor.start_monitoring(exec_on_start=False)

        monitor._scheduler.add_job.assert_called_once_with(
            monitor._monitoring_process,
            "interval",
            seconds=monitor._config.MONITOR_CONFIG["monitoring_job_interval"],
            next_run_time=undefined,
            replace_existing=False,
            id="_monitor_process",
        )

    @pytest.mark.asyncio
    async def start_monitor_job_with_job_id_already_executing_test(self, monitor):
        job_id = "some-duplicated-id"
        exception_instance = ConflictingIdError(job_id)
        monitor._scheduler.add_job = Mock(side_effect=exception_instance)

        try:
            await monitor.start_monitoring(exec_on_start=False)
        except ConflictingIdError:
            monitor._scheduler.add_job.assert_called_once_with(
                monitor._monitoring_process,
                "interval",
                seconds=monitor._config.MONITOR_CONFIG["monitoring_job_interval"],
                next_run_time=undefined,
                replace_existing=False,
                id="_monitor_process",
            )

    @pytest.mark.asyncio
    async def monitoring_process_ok_test(self, monitor):
        monitor._tunnel_count_check = CoroutineMock()

        await monitor._monitoring_process()

        monitor._tunnel_count_check.assert_awaited()

    @pytest.mark.asyncio
    async def tunnel_count_check_ok_test(self, monitor, make_rpc_response, logger):
        response_status = HTTPStatus.OK
        gateway_status_first_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 423),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        expected_response_first_inteval = make_rpc_response(
            request_id=uuid_, body=gateway_status_first_interval, status=response_status
        )
        gateway_status_second_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 323),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        expected_response_second_interval = make_rpc_response(
            request_id=uuid_, body=gateway_status_second_interval, status=response_status
        )
        monitor._velocloud_repository.get_network_gateway_status_list = CoroutineMock(
            side_effect=[expected_response_first_inteval, expected_response_second_interval]
        )
        monitor._servicenow_repository._check_servicenow = CoroutineMock()

        await monitor._tunnel_count_check(monitor._config.MONITOR_CONFIG["monitored_velocloud_hosts"][0])

        monitor._velocloud_repository.get_network_gateway_status_list.assert_awaited()
        monitor._check_servicenow.assert_awaited()

    @pytest.mark.asyncio
    async def build_pair_statuses_ok_test(self, monitor):
        gateway_status_first_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 423),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        gateway_status_second_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 323),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        expected_result = GatewayPair(gateway_status_first_interval, gateway_status_second_interval)

        result = monitor._build_pair_statuses(gateway_status_first_interval, gateway_status_second_interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def check_average_tunnel_count_ok_test(self, monitor):
        gateway_status_second_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 323),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        gateway_status_first_interval = GatewayList(
            Gateway("mettel.velocloud.net", 2, 423),
            Gateway("mettel.velocloud.net", 1, 100),
        )
        gateway_pairs = monitor._build_pair_statuses(gateway_status_first_interval, gateway_status_second_interval)
        expected_result = GatewayList(
            Gateway("mettel.velocloud.net", 2, 323)
        )

        unhealthy_gateways = monitor._check_average_tunnel_count(gateway_pairs)

        assert unhealthy_gateways == expected_result

    @pytest.mark.asyncio
    async def tunnel_count_less_percentual_value_ok_test(self, monitor):
        gateway_status_first_interval = 423
        gateway_status_second_interval = 323

        percentual_loss = (1 - (gateway_status_second_interval / gateway_status_first_interval)) * 100
        expected_result = percentual_loss > monitor._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]

        result = monitor._tunnel_count_less(gateway_status_first_interval, gateway_status_second_interval)

        assert result == expected_result
