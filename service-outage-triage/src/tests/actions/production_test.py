import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions.production import ProductionAction
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import production as production_module
from config import testconfig


class TestProductionAction:

    def instance_test(self):
        event_bus = Mock()
        config = Mock()

        production_action = ProductionAction(event_bus, config)

        assert production_action._event_bus == event_bus
        assert production_action._config == config

    @pytest.mark.asyncio
    async def post_triage_note_test(self):
        event_bus = Mock()
        config = Mock()
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        test_note = 'Test Note'
        ticket_id = 123

        production_action = ProductionAction(event_bus, config)
        production_action._ticket_object_to_string = Mock(return_value=test_note)
        production_action._post_ticket_request = CoroutineMock()

        await production_action.post_triage_note(test_dict, ticket_id)

        production_action._ticket_object_to_string.assert_called_once_with(test_dict)
        production_action._post_ticket_request.assert_awaited_once_with("Triage", ticket_id, test_note)

    @pytest.mark.asyncio
    async def post_event_note_test(self):
        event_bus = Mock()
        config = Mock()
        test_note = 'Test Note'
        ticket_id = 123

        production_action = ProductionAction(event_bus, config)
        production_action._post_ticket_request = CoroutineMock()

        await production_action.post_event_note(test_note, ticket_id)

        production_action._post_ticket_request.assert_awaited_once_with("Events", ticket_id, test_note)

    @pytest.mark.asyncio
    async def post_ticket_request_test(self):
        config = testconfig
        environment = 'production'

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = environment

        test_note = 'Test Note'
        ticket_id = 123

        append_ticket = {'ticket_appended': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[append_ticket, send_to_slack])

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_side_effect = [uuid_1, uuid_2]

        production_action = ProductionAction(event_bus, config)
        with patch.object(production_module, 'uuid', side_effect=uuid_side_effect):
            with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
                await production_action._post_ticket_request("Triage", ticket_id, test_note)

        event_bus.rpc_request.assert_has_awaits([

            call(
                'bruin.ticket.note.append.request',
                json.dumps({
                    'request_id': uuid_1,
                    'ticket_id': ticket_id,
                    'note': test_note
                }),
                timeout=15,
            ),
            call(
                'notification.slack.request',
                json.dumps({
                    'request_id': uuid_2,
                    'message': (
                        'Triage appended to ticket: '
                        f'https://app.bruin.com/helpdesk?clientId=85940&ticketId={ticket_id}, in {environment}'
                    )
                }),
                timeout=10,
            )
        ], any_order=False
        )

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        config = Mock()

        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}

        production_action = ProductionAction(event_bus, config)
        ticket_note = production_action._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'
