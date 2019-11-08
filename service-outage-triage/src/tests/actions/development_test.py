import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch
from collections import OrderedDict

import pytest
from application.actions.development import DevelopmentAction
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import development as development_module
from config import testconfig


class TestProductionAction:

    def instance_test(self):
        event_bus = Mock()
        config = Mock()

        development_action = DevelopmentAction(event_bus, config)

        assert development_action._event_bus == event_bus
        assert development_action._config == config

    @pytest.mark.asyncio
    async def run_triage_action_test(self):
        config = testconfig

        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        ticket_note_as_email_object = {'email_object': "Something happened"}
        send_to_slack = {'slack_sent': 'Success'}

        environment = 'dev'
        ticket_id = 123

        uuid_1 = uuid()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_note_as_email_object, send_to_slack])

        development_action = DevelopmentAction(event_bus, config)
        development_action._ticket_object_to_email_obj = Mock(return_value=ticket_note_as_email_object)

        with patch.object(development_module, 'uuid', return_value=uuid_1):
            await development_action.run_triage_action(test_dict, ticket_id)

        event_bus.rpc_request.assert_has_awaits([
            call(
                'notification.email.request',
                json.dumps(ticket_note_as_email_object),
                timeout=10,
            ),
            call(
                'notification.slack.request',
                json.dumps({
                    'request_id': uuid_1,
                    'message': (
                        'Triage appended to ticket: '
                        f'https://app.bruin.com/helpdesk?clientId=85940&ticketId={ticket_id}, in {environment}'
                    )
                }),
                timeout=10,
            )
        ], any_order=False
        )

    def ticket_object_to_email_obj_test(self):
        event_bus = Mock()
        config = testconfig
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Last Edge Online"] = 'test time'
        ticket_dict['Events URL'] = 'event.com'
        development_action = DevelopmentAction(event_bus, config)
        email = development_action._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def ticket_object_to_email_obj_no_events_test(self):
        event_bus = Mock()
        config = testconfig
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        development_action = DevelopmentAction(event_bus, config)
        email = development_action._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
