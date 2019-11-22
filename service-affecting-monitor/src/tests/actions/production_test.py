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
        logger = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = Mock()

        production_action = ProductionAction(logger, event_bus, template_renderer, config)

        assert production_action._logger == logger
        assert production_action._event_bus == event_bus
        assert production_action._config == config

    @pytest.mark.asyncio
    async def run_action_ticket_exists_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[{'ticketIds': {'ticketIds': [123]}}, 'Note Posted',
                                                           'Slack Sent'])
        logger = Mock()
        template_renderer = Mock()

        device = {
            "serial": 'VC05200033383',
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "email": "fake@gmail.com",
            "phone": "111-111-1111",
            "name": "Fake Guy"
        }

        config = testconfig
        environment = 'production'

        custom_triage_config = config.ENV_CONFIG.copy()
        custom_triage_config['environment'] = environment

        client_id = '85940'
        trouble = 'LATENCY'
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
        ticket_dict = {'test': 'dict'}

        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        production_action._ticket_existence = CoroutineMock(return_value=True)
        production_action._ticket_object_to_string = Mock(return_value='Some string object')

        await production_action.run_action(device, edges_to_report, trouble, ticket_dict)

        production_action._ticket_existence.assert_awaited_once_with(client_id,
                                                                     edges_to_report['edge_info']['edges'][
                                                                                     'serialNumber'], trouble)
        production_action._ticket_object_to_string.assert_not_called()
        event_bus.rpc_request.assert_not_called()

    @pytest.mark.asyncio
    async def run_action_ticket_not_exists_test(self):
        event_bus = Mock()
        ticket_creation = {'ticketIds': {'ticketIds': [123]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_creation, 'Note Posted',
                                                           'Slack Sent'])
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        environment = 'production'

        custom_triage_config = config.ENV_CONFIG.copy()
        custom_triage_config['environment'] = environment

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_side_effect = [uuid_1, uuid_2, uuid_3]

        device = {
            "serial": 'VC05200033383',
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "email": "fake@gmail.com",
            "phone": "111-111-1111",
            "name": "Fake Guy"
        }

        client_id = '85940'
        trouble = 'LATENCY'
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
        ticket_dict = {'test': 'dict'}
        ticket_str = 'Some string object'
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        production_action._ticket_existence = CoroutineMock(return_value=False)
        production_action._ticket_object_to_string = Mock(return_value=ticket_str)

        with patch.object(production_module, 'uuid', side_effect=uuid_side_effect):
            with patch.dict(config.ENV_CONFIG, custom_triage_config):
                await production_action.run_action(device, edges_to_report, trouble, ticket_dict)

        production_action._ticket_existence.assert_awaited_once_with(client_id, edges_to_report['edge_info']['edges'][
                                                                                 'serialNumber'], trouble)

        event_bus.rpc_request.assert_has_awaits([

            call(
                "bruin.ticket.creation.request",
                json.dumps({
                    "request_id": uuid_1,
                    "clientId": client_id,
                    "category": "VAS",
                    "services": [
                        {
                            "serviceNumber": device['serial']
                        }
                    ],
                    "contacts": [
                        {
                            "email": device['email'],
                            "phone": device['phone'],
                            "name": device['name'],
                            "type": "site"
                        },
                        {
                            "email": device['email'],
                            "phone": device['phone'],
                            "name": device['name'],
                            "type": "ticket"
                        }
                    ]
                }),
                timeout=30,
            ),
            call(
                "bruin.ticket.note.append.request",
                json.dumps({
                    'request_id': uuid_2,
                    'ticket_id': ticket_creation['ticketIds']['ticketIds'][0],
                    'note': ticket_str
                }),
                timeout=15,
            ),
            call(
                "notification.slack.request",
                json.dumps({'request_id': uuid_3,
                            'message': f'Ticket created with ticket id: {ticket_creation["ticketIds"]["ticketIds"][0]}'
                                       f'\nhttps://app.bruin.com/helpdesk?clientId=85940&'
                                       f'ticketId={ticket_creation["ticketIds"]["ticketIds"][0]} , in '
                                       f'{environment}'
                            }),
                timeout=10,
            )
        ], any_order=False
        )

    @pytest.mark.asyncio
    async def ticket_existence_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await production_action._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is True
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_wrong_trouble_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details, 'Slack Sent'])
        ticket_exists = await production_action._ticket_existence(85940, 'VC05200026138', 'PACKET_LOSS')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_wrong_serial_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026137'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await production_action._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_no_details_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{'otherDetails': None}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await production_action._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_no_notes_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": None}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await production_action._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        logger = Mock()
        template_renderer = Mock()
        config = testconfig
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        production_action = ProductionAction(logger, event_bus, template_renderer, config)
        ticket_note = production_action._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'
