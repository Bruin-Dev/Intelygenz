from datetime import datetime
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from application.actions import monitoring as monitoring_module
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
        logger,
        event_bus,
        scheduler,
        servicenow_repository,
        velocloud_repository,
        notifications_repository,
        utils_repository,
    ):
        assert monitor._event_bus is event_bus
        assert monitor._logger is logger
        assert monitor._scheduler is scheduler
        assert monitor._config is testconfig
        assert monitor._velocloud_repository is velocloud_repository
        assert monitor._servicenow_repository is servicenow_repository
        assert monitor._notifications_repository is notifications_repository
        assert monitor._utils_repository is utils_repository

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
    async def monitoring_process_test(self, monitor):
        monitor._process_host = CoroutineMock()

        await monitor._monitoring_process()

        monitor._process_host.assert_awaited()

    @pytest.mark.asyncio
    async def process_host_ok_test(self, monitor, make_gateway, make_gateway_metrics, make_rpc_response):
        host = monitor._config.MONITOR_CONFIG["monitored_velocloud_hosts"][0]
        gateways = [make_gateway(id=1), make_gateway(id=2)]
        gateway_metrics_1 = make_gateway_metrics(tunnel_count={"average": 100, "min": 100})
        gateway_metrics_2 = make_gateway_metrics(tunnel_count={"average": 100, "min": 50})

        gateways_response = make_rpc_response(request_id=uuid_, body=gateways, status=HTTPStatus.OK)
        gateway_metrics_response_1 = make_rpc_response(request_id=uuid_, body=gateway_metrics_1, status=HTTPStatus.OK)
        gateway_metrics_response_2 = make_rpc_response(request_id=uuid_, body=gateway_metrics_2, status=HTTPStatus.OK)

        monitor._velocloud_repository.get_network_gateway_list = CoroutineMock(return_value=gateways_response)
        monitor._velocloud_repository.get_gateway_status_metrics = CoroutineMock(
            side_effect=[gateway_metrics_response_1, gateway_metrics_response_2]
        )
        monitor._report_servicenow_incident = CoroutineMock()

        await monitor._process_host(host)

        monitor._velocloud_repository.get_network_gateway_list.assert_awaited_once_with(host)
        assert monitor._velocloud_repository.get_gateway_status_metrics.call_count == len(gateways)
        monitor._report_servicenow_incident.assert_awaited_once()

    @pytest.mark.asyncio
    async def report_servicenow_incident_test(
        self, monitor, make_gateway_with_metrics, make_rpc_response, make_report_incident_response
    ):
        gateway = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 50})

        body_1 = make_report_incident_response(state="inserted")
        body_2 = make_report_incident_response(state="ignored")
        body_3 = make_report_incident_response(state="reopened")

        response_1 = make_rpc_response(request_id=uuid_, body=body_1, status=HTTPStatus.OK)
        response_2 = make_rpc_response(request_id=uuid_, body=body_2, status=HTTPStatus.OK)
        response_3 = make_rpc_response(request_id=uuid_, body=body_3, status=HTTPStatus.OK)
        response_4 = make_rpc_response(request_id=uuid_, body=None, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        responses = [response_1, response_2, response_3, response_4]

        monitor._servicenow_repository.report_incident = CoroutineMock(side_effect=responses)
        monitor._notifications_repository.send_slack_message = CoroutineMock()

        await monitor._report_servicenow_incident(gateway)
        await monitor._report_servicenow_incident(gateway)
        await monitor._report_servicenow_incident(gateway)
        await monitor._report_servicenow_incident(gateway)

        assert monitor._servicenow_repository.report_incident.call_count == len(responses)
        assert monitor._notifications_repository.send_slack_message.call_count == len(responses)

    def filter_gateways_with_metrics_test(self, monitor, make_gateway_with_metrics):
        gateway_1 = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 100})
        gateway_2 = make_gateway_with_metrics(id=2)
        gateways = [gateway_1, gateway_2]
        expected_result = [gateway_1]

        result = monitor._filter_gateways_with_metrics(gateways)
        assert result == expected_result

    def has_metrics_test(self, monitor, make_gateway_with_metrics):
        gateway = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 100})
        result = monitor._has_metrics(gateway)
        assert result is True

        gateway = make_gateway_with_metrics(id=2, tunnel_count={"average": 0, "min": 0})
        result = monitor._has_metrics(gateway)
        assert result is False

        gateway = make_gateway_with_metrics(id=3, tunnel_count={})
        result = monitor._has_metrics(gateway)
        assert result is False

        gateway = make_gateway_with_metrics(id=4)
        result = monitor._has_metrics(gateway)
        assert result is False

    def get_unhealthy_gateways_test(self, monitor, make_gateway_with_metrics):
        gateway_1 = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 100})
        gateway_2 = make_gateway_with_metrics(id=2, tunnel_count={"average": 100, "min": 50})
        gateways = [gateway_1, gateway_2]
        expected_result = [gateway_2]

        result = monitor._get_unhealthy_gateways(gateways)
        assert result == expected_result

    def is_tunnel_count_within_threshold_test(self, monitor, make_gateway_with_metrics):
        gateway = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 100})
        result = monitor._is_tunnel_count_within_threshold(gateway)
        assert result is True

        gateway = make_gateway_with_metrics(id=2, tunnel_count={"average": 100, "min": 50})
        result = monitor._is_tunnel_count_within_threshold(gateway)
        assert result is False
