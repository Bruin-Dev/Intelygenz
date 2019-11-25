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


class TestDevelopmentAction:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = Mock()

        development_action = DevelopmentAction(logger, event_bus, template_renderer, config)

        assert development_action._logger == logger
        assert development_action._event_bus == event_bus
        assert development_action._config == config

    @pytest.mark.asyncio
    async def run_triage_action_test(self):
        logger = Mock()

        config = testconfig

        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        ticket_note_as_email = {'email_object': "Something happened"}
        email_sent = 'Email sent'
        send_to_slack = {'slack_sent': 'Success'}

        environment = 'dev'
        ticket_id = 123

        uuid_1 = uuid()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[email_sent, send_to_slack])

        template_renderer = Mock()
        template_renderer._ticket_object_to_email_obj = Mock(return_value=ticket_note_as_email)

        development_action = DevelopmentAction(logger, event_bus, template_renderer, config)

        with patch.object(development_module, 'uuid', return_value=uuid_1):
            await development_action.run_triage_action(test_dict, ticket_id)

        event_bus.rpc_request.assert_has_awaits([
            call(
                'notification.email.request',
                json.dumps(ticket_note_as_email),
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
