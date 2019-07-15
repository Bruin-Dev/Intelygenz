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
    async def request_edges_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)

        await edge_monitoring._request_edges()
        assert event_bus.publish_message.called
        assert "edge.status.request" in event_bus.publish_message.call_args[0][0]

    @pytest.mark.asyncio
    async def receive_edge_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge = {"request_id": 1234, 'edge_id': {'host': 'some_host'}, 'edge_info': 'Some edge data'}

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._compose_email_object = Mock(return_value=edge)

        await edge_monitoring.receive_edge(json.dumps(edge))
        assert event_bus.publish_message.called
        assert edge_monitoring._compose_email_object.called
        assert event_bus.publish_message.call_args[0][1] == json.dumps(edge)

    @pytest.mark.asyncio
    async def start_edge_monitor_job_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
        edge_monitoring._request_edges = Mock()
        await edge_monitoring.start_edge_monitor_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is edge_monitoring._request_edges
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
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        "link": {
                            "interface": "GE1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        "link": {
                            "interface": "GE2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }

        email = edge_monitoring._compose_email_object(edges_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_one_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
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
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        "link": {
                            "interface": "GE1",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }

        email = edge_monitoring._compose_email_object(edges_to_report)

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
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": []
            }
        }

        email = edge_monitoring._compose_email_object(edges_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_null_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, scheduler, service_id, config)
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
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [{"link": None}]
            }
        }

        email = edge_monitoring._compose_email_object(edges_to_report)

        assert 'Edge Monitoring' in email["email_data"]["subject"]
        assert config["edge_monitoring"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
