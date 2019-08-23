from unittest.mock import Mock

import pytest
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from apscheduler.util import undefined
from asynctest import CoroutineMock

from config import testconfig


class TestServiceAffectingMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        assert isinstance(service_affecting_monitor, ServiceAffectingMonitor)
        assert service_affecting_monitor._event_bus is event_bus
        assert service_affecting_monitor._logger is logger
        assert service_affecting_monitor._scheduler is scheduler
        assert service_affecting_monitor._service_id == service_id
        assert service_affecting_monitor._config is config

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_true_exec_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._service_affecting_monitor_process = CoroutineMock()
        await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_affecting_monitor._service_affecting_monitor_process
        assert "interval" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == 60

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_false_exec_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._service_affecting_monitor_process = CoroutineMock()
        await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=False)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_affecting_monitor._service_affecting_monitor_process
        assert "interval" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == 60
        assert scheduler.add_job.call_args[1]['next_run_time'] == undefined

    @pytest.mark.asyncio
    async def _service_affecting_monitor_process_test(self):
        event_bus = Mock()
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 121,
                        'serviceGroups': ['PUBLIC_WIRELESS']
                    },
                    {
                        'bestLatencyMsRx': 60,
                        'bestLatencyMsTx': 20,
                        'serviceGroups': ['PUBLIC_WIRED']
                    },

                ]
            }
        }
        event_bus.rpc_request = CoroutineMock(return_value=edges_to_report)
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._latency_check = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        assert event_bus.rpc_request.called
        assert service_affecting_monitor._latency_check.called

    @pytest.mark.asyncio
    async def latency_check_wireless_and_wired_ko_test(self):
        event_bus = Mock()
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 121,
                        'serviceGroups': ['PUBLIC_WIRELESS']
                    },
                    {
                        'bestLatencyMsRx': 60,
                        'bestLatencyMsTx': 20,
                        'serviceGroups': ['PUBLIC_WIRED']
                    },

                ]
            }
        }
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][0])

        assert service_affecting_monitor._notify_trouble.called
        assert service_affecting_monitor._notify_trouble.mock_calls[0][1][0] == edges_to_report
        assert service_affecting_monitor._notify_trouble.mock_calls[0][1][2] == 'Latency'
        assert service_affecting_monitor._notify_trouble.mock_calls[0][1][3] == 120

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][1])

        assert service_affecting_monitor._notify_trouble.mock_calls[1][1][0] == edges_to_report
        assert service_affecting_monitor._notify_trouble.mock_calls[1][1][2] == 'Latency'
        assert service_affecting_monitor._notify_trouble.mock_calls[1][1][3] == 50

    @pytest.mark.asyncio
    async def latency_check_wireless_and_wired_ok_test(self):
        event_bus = Mock()
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 14,
                        'serviceGroups': ['PUBLIC_WIRELESS']
                    },
                    {
                        'bestLatencyMsRx': 49,
                        'bestLatencyMsTx': 20,
                        'serviceGroups': ['PUBLIC_WIRED']
                    },

                ]
            }
        }
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][0])
        assert service_affecting_monitor._notify_trouble.called is False

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][1])
        assert service_affecting_monitor._notify_trouble.called is False

    @pytest.mark.asyncio
    async def latency_check_wireless_and_wired_none_test(self):
        event_bus = Mock()
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 14,
                        'serviceGroups': ['None']
                    },
                    {
                        'bestLatencyMsRx': 49,
                        'bestLatencyMsTx': 20,
                        'serviceGroups': ['None']
                    },

                ]
            }
        }
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][0])
        assert service_affecting_monitor._notify_trouble.called is False

        await service_affecting_monitor._latency_check(edges_to_report, edges_to_report["edge_info"]['links'][1])
        assert service_affecting_monitor._notify_trouble.called is False

    @pytest.mark.asyncio
    async def _notify_trouble_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value="Email Sent")
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._compose_email_object = Mock(return_value='Some email object')

        await service_affecting_monitor._notify_trouble('Some Edge Status', 'Some Link Info', 'LATENCY', 120)

        assert service_affecting_monitor._compose_email_object.called
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def _notify_trouble_none_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value="Email Sent")
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.MONITOR_CONFIG['environment'] = 'None'
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        service_affecting_monitor._compose_email_object = Mock(return_value='Some email object')

        await service_affecting_monitor._notify_trouble('Some Edge Status', 'Some Link Info', 'LATENCY', 120)

        assert service_affecting_monitor._compose_email_object.called is False
        assert event_bus.rpc_request.called is False

    def compose_email_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, service_id, config)
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }

        email = service_affecting_monitor._compose_email_object(edges_to_report,
                                                                edges_to_report['edge_info']['links'][0],
                                                                'LATENCY', 120)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
