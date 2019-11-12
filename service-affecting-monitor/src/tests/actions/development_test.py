from unittest.mock import Mock

import pytest
from application.actions.development import DevelopmentAction
from asynctest import CoroutineMock

from config import testconfig


class TestDevelopmentAction:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        config = Mock()

        development_action = DevelopmentAction(logger, event_bus, config)

        assert development_action._logger == logger
        assert development_action._event_bus == event_bus
        assert development_action._config == config

    @pytest.mark.asyncio
    async def run_action_test(self):
        logger = Mock()
        config = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value="Email Sent")

        device = Mock()
        edge_status = 'Some Edge Status'
        trouble = 'LATENCY'
        ticket_dict = {'test': 'dict'}

        development_action = DevelopmentAction(logger, event_bus, config)

        development_action._compose_email_object = Mock(return_value='Some email object')

        await development_action.run_action(device, edge_status, trouble, ticket_dict)

        development_action._compose_email_object.assert_called_once_with(edge_status, trouble, ticket_dict)
        event_bus.rpc_request.assert_awaited_once()

    def ticket_object_to_email_obj_test(self):
        logger = Mock()
        event_bus = Mock()
        config = testconfig

        development_action = DevelopmentAction(logger, event_bus, config)

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
        email = development_action._compose_email_object(edges_to_report, 'Latency', test_dict)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
