from unittest.mock import Mock

import pytest
from application.actions.service_outage_monitor import ServiceOutageMonitor
from apscheduler.util import undefined
from asynctest import CoroutineMock

from config import testconfig


class TestServiceOutageMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        assert isinstance(service_outage_monitor, ServiceOutageMonitor)
        assert service_outage_monitor._event_bus is event_bus
        assert service_outage_monitor._logger is logger
        assert service_outage_monitor._scheduler is scheduler
        assert service_outage_monitor._service_id == service_id
        assert service_outage_monitor._config is config

    @pytest.mark.asyncio
    async def start_service_outage_monitor_job_true_exec_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._service_outage_monitor_process = CoroutineMock()
        await service_outage_monitor.start_service_outage_monitor_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_outage_monitor._service_outage_monitor_process
        assert "interval" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == 900

    @pytest.mark.asyncio
    async def start_service_outage_monitor_job_false_exec_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._service_outage_monitor_process = CoroutineMock()
        await service_outage_monitor.start_service_outage_monitor_job(exec_on_start=False)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_outage_monitor._service_outage_monitor_process
        assert "interval" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == 900
        assert scheduler.add_job.call_args[1]['next_run_time'] == undefined

    @pytest.mark.asyncio
    async def service_outage_monitor_process_offline_dev_test(self):
        event_bus = Mock()
        edge_list = {'edges': {'edge': 'Some edge id'}}
        edge_status = {'edge_id': 'Some edge id', 'edge_info': {'edges': {'edgeState': 'OFFLINE'}}}
        edge_event = {'edge_events': 'Some event info'}
        email_sent = {'email_sent': 'Success'}
        event_bus.rpc_request = CoroutineMock(side_effect=[edge_list, edge_status, edge_event, email_sent])
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._compose_email_object = Mock(return_value='Some email object')
        await service_outage_monitor._service_outage_monitor_process()

        assert logger.error.called
        assert event_bus.rpc_request.called
        assert service_outage_monitor._compose_email_object.called
        assert event_bus.rpc_request.mock_calls[2][1][0] == "alert.request.event.edge"
        assert event_bus.rpc_request.mock_calls[3][1][0] == "notification.email.request"

    @pytest.mark.asyncio
    async def service_outage_monitor_process_connected_test(self):
        event_bus = Mock()
        edge_list = {'edges': {'edge': 'Some edge id'}}
        edge_status = {'edge_id': 'Some edge id', 'edge_info': {'edges': {'edgeState': 'CONNECTED'}}}
        edge_event = {'edge_events': 'Some event info'}
        event_bus.rpc_request = CoroutineMock(side_effect=[edge_list, edge_status, edge_event])
        logger = Mock()
        logger.info = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._compose_email_object = Mock(return_value='Some email object')

        await service_outage_monitor._service_outage_monitor_process()

        assert logger.info.called
        assert event_bus.rpc_request.called
        assert service_outage_monitor._compose_email_object.called is False
        assert event_bus.rpc_request.call_args[0][0] == "edge.status.request"

    @pytest.mark.asyncio
    async def service_outage_monitor_process_other_test(self):
        event_bus = Mock()
        edge_list = {'edges': {'edge': 'Some edge id'}}
        edge_status = {'edge_id': 'Some edge id', 'edge_info': {'edges': {'edgeState': 'DISCONNECTED'}}}
        edge_event = {'edge_events': 'Some event info'}
        event_bus.rpc_request = CoroutineMock(side_effect=[edge_list, edge_status, edge_event])
        logger = Mock()
        logger.info = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._compose_email_object = Mock(return_value='Some email object')

        await service_outage_monitor._service_outage_monitor_process()

        assert event_bus.rpc_request.called
        assert service_outage_monitor._compose_email_object.called is False
        assert event_bus.rpc_request.call_args[0][0] == "edge.status.request"

    def find_recent_occurence_of_event_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        event_list = [{'event': 'EDGE_ALIVE',
                       'eventTime': '2019-07-30 06:38:00+00:00',
                       'message': 'Edge is back up'},
                      {'event': 'LINK_ALIVE',
                       'eventTime': '2019-07-30 4:26:00+00:00',
                       'message': 'Link GE2 is no longer DEAD'},
                      {'event': 'EDGE_ALIVE',
                       'eventTime': '2019-07-29 06:38:00+00:00',
                       'message': 'Edge is back up'}
                      ]
        edge_online_time = service_outage_monitor._find_recent_occurence_of_event(event_list, 'EDGE_ALIVE')
        assert edge_online_time == '2019-07-30 06:38:00+00:00'
        link_online_time = service_outage_monitor._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                                  'Link GE2 is no longer DEAD')
        assert link_online_time == '2019-07-30 4:26:00+00:00'
        link_dead_time = service_outage_monitor._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                                'Link GE1 is no longer DEAD')
        assert link_dead_time is None

    def compose_email_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._find_recent_occurence_of_event = Mock()
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
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        events_to_report = {'events': {'data': 'Some Event Info'}}

        email = service_outage_monitor._compose_email_object(edges_to_report, events_to_report)

        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert service_outage_monitor._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_one_links_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._find_recent_occurence_of_event = Mock()

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
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        events_to_report = {'events': {'data': 'Some Event Info'}}

        email = service_outage_monitor._compose_email_object(edges_to_report, events_to_report)

        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert service_outage_monitor._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_no_links_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._find_recent_occurence_of_event = Mock()

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
                "links": []
            }
        }
        events_to_report = {'events': {'data': 'Some Event Info'}}

        email = service_outage_monitor._compose_email_object(edges_to_report, events_to_report)

        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert service_outage_monitor._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_null_links_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, service_id, config)
        service_outage_monitor._find_recent_occurence_of_event = Mock()

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
                "links": [{"link": None}]
            }
        }
        events_to_report = {'events': {'data': 'Some Event Info'}}

        email = service_outage_monitor._compose_email_object(edges_to_report, events_to_report)

        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert service_outage_monitor._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]
