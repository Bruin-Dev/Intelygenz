from unittest.mock import Mock
from config import testconfig
from application.repositories.template_management import TemplateRenderer
import base64


class TestTemplateRenderer:

    def instantiation_test(self):
        mock_service_id = Mock()
        config = testconfig
        test_repo = TemplateRenderer(config)
        assert test_repo._config == config

    def ticket_object_to_email_obj_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123
        template_renderer = TemplateRenderer(config)

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
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'Latency', test_dict)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        base = "src/templates/images/{}"
        kwargs = dict(logo="logo.png",
                      header="header.jpg")
        config = testconfig
        template_renderer = TemplateRenderer(config)
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
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'LATENCY', test_dict)

        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')

    def compose_email_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        template_renderer = TemplateRenderer(config)

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
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'LATENCY', test_dict)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
