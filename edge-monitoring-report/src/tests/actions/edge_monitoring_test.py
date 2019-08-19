import json
from unittest.mock import Mock

import pytest
from application.actions.edge_monitoring import EdgeMonitoring
from asynctest import CoroutineMock

from config import testconfig


class TestEdgeMonitoring:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        assert isinstance(edge_monitoring, EdgeMonitoring)
        assert edge_monitoring._event_bus is event_bus
        assert edge_monitoring._logger is logger
        assert edge_monitoring._scheduler is scheduler
        assert edge_monitoring._service_id == service_id
        assert edge_monitoring._config is config

    @pytest.mark.asyncio
    async def request_edge_events_and_status_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._compose_email_object = Mock(return_value="Email Object")

        await edge_monitoring._request_edge_events_and_status()
        assert event_bus.rpc_request.called
        assert edge_monitoring._compose_email_object.called
        assert event_bus.publish_message.called
        assert "notification.email.request" in event_bus.publish_message.call_args[0][0]
        assert event_bus.publish_message.call_args[0][1] == json.dumps("Email Object")

    def find_recent_occurence_of_event_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
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
        edge_online_time = edge_monitoring._find_recent_occurence_of_event(event_list, 'EDGE_ALIVE')
        assert edge_online_time == '2019-07-30 06:38:00+00:00'
        link_online_time = edge_monitoring._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                           'Link GE2 is no longer DEAD')
        assert link_online_time == '2019-07-30 4:26:00+00:00'
        link_dead_time = edge_monitoring._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                         'Link GE1 is no longer DEAD')
        assert link_dead_time is None

    @pytest.mark.asyncio
    async def start_edge_monitor_job_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._request_edge_events_and_status = Mock()
        await edge_monitoring.start_edge_monitor_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is edge_monitoring._request_edge_events_and_status
        assert "cron" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['hour'] == 0

    def compose_email_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._find_recent_occurence_of_event = Mock()
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

        email = edge_monitoring._compose_email_object(edges_to_report, events_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert edge_monitoring._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_one_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._find_recent_occurence_of_event = Mock()

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

        email = edge_monitoring._compose_email_object(edges_to_report, events_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_no_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._find_recent_occurence_of_event = Mock()

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

        email = edge_monitoring._compose_email_object(edges_to_report, events_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert edge_monitoring._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_null_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._find_recent_occurence_of_event = Mock()

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

        email = edge_monitoring._compose_email_object(edges_to_report, events_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert edge_monitoring._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]
