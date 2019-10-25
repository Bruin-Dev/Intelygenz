from unittest.mock import Mock
from config import testconfig as config
from application.repositories.template_management import TemplateRenderer
from config import testconfig
import base64


class TestTemplateRenderer:

    def instantiation_test(self):
        mock_service_id = Mock()
        test_repo = TemplateRenderer(mock_service_id, config)
        assert test_repo._config == config
        assert test_repo._service_id is mock_service_id

    def compose_email_object_test(self):
        mock_service_id = Mock()
        test_repo = TemplateRenderer(mock_service_id, config)
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
        email = test_repo._compose_email_object(edges_to_report, events_to_report)
        assert email is not None
        assert isinstance(email, dict) is True
        assert f"notification.email.response.{mock_service_id}" == email["response_topic"]

    def compose_email_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123
        template_renderer = TemplateRenderer(service_id, config)
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
        template_renderer._find_recent_occurence_of_event = Mock()
        email = template_renderer._compose_email_object(edges_to_report, events_to_report)
        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert template_renderer._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        mock_service_id = Mock()
        base = "src/templates/images/{}"
        kwargs = dict(logo="logo.png",
                      header="header.jpg")
        test_repo = TemplateRenderer(mock_service_id, config)
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
        email = test_repo._compose_email_object(edges_to_report, events_to_report, **kwargs)
        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')

    def compose_email_no_links_test(self):
        config = testconfig
        service_id = 123
        template_renderer = TemplateRenderer(service_id, config)
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
        template_renderer._find_recent_occurence_of_event = Mock()
        email = template_renderer._compose_email_object(edges_to_report, events_to_report)
        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert template_renderer._find_recent_occurence_of_event.called
        assert template_renderer._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_one_links_test(self):
        config = testconfig
        service_id = 123
        template_renderer = TemplateRenderer(service_id, config)
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

        template_renderer._find_recent_occurence_of_event = Mock()
        template_renderer._find_recent_occurence_of_event.return_value = "message"
        email = template_renderer._compose_email_object(edges_to_report, events_to_report)
        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert template_renderer._find_recent_occurence_of_event.called
        assert template_renderer._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_null_links_test(self):
        config = testconfig
        service_id = 123
        template_renderer = TemplateRenderer(service_id, config)
        template_renderer._find_recent_occurence_of_event = Mock()
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
        template_renderer._find_recent_occurence_of_event = Mock()
        email = template_renderer._compose_email_object(edges_to_report, events_to_report)
        assert 'Service outage monitor' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert template_renderer._find_recent_occurence_of_event.called
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def find_recent_occurence_of_event_test(self):
        service_id = 123
        config = testconfig
        template_renderer = TemplateRenderer(service_id, config)
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
        edge_online_time = template_renderer._find_recent_occurence_of_event(event_list, 'EDGE_ALIVE')
        assert edge_online_time == '2019-07-30 06:38:00+00:00'
        link_online_time = template_renderer._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                             'Link GE2 is no longer DEAD')
        assert link_online_time == '2019-07-30 4:26:00+00:00'
        link_dead_time = template_renderer._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                           'Link GE1 is no longer DEAD')
        assert link_dead_time is None
