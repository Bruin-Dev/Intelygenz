import json
from collections import OrderedDict
from unittest.mock import Mock

import pytest
from application.actions.service_outage_triage import ServiceOutageTriage
from asynctest import CoroutineMock

from config import testconfig


class TestServiceOutageTriage:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        assert isinstance(edge_monitoring, ServiceOutageTriage)
        assert edge_monitoring._event_bus is event_bus
        assert edge_monitoring._logger is logger
        assert edge_monitoring._scheduler is scheduler
        assert edge_monitoring._service_id == service_id
        assert edge_monitoring._config is config

    @pytest.mark.asyncio
    async def start_service_outage_triage_job_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._poll_tickets = Mock()
        await service_outage_triage.start_service_outage_triage_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_outage_triage._poll_tickets
        assert 'interval' in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['minute'] == 1

    @pytest.mark.asyncio
    async def poll_tickets_ok_none_note_test(self):
        event_bus = Mock()
        tickets = {'tickets': {"responses": [{"ticketID": 3521039}]}}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200028729'}],
                          "ticketNotes": [{"noteValue": None}]}}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        rpc_returns = [tickets, ticket_details, edge_status, edge_event, append_ticket]
        event_bus.rpc_request = CoroutineMock(side_effect=rpc_returns)
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._compose_ticket_note_object = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._compose_ticket_note_object.called

    @pytest.mark.asyncio
    async def poll_tickets_ok_other_info_test(self):
        event_bus = Mock()
        tickets = {'tickets': {"responses": [{"ticketID": 3521039}]}}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200028729'}],
                          "ticketNotes": [{"noteValue": 'test info'}]}}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        rpc_returns = [tickets, ticket_details, edge_status, edge_event, append_ticket]
        event_bus.rpc_request = CoroutineMock(side_effect=rpc_returns)
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._compose_ticket_note_object = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._compose_ticket_note_object.called

    @pytest.mark.asyncio
    async def poll_tickets_ko_triage_exists_test(self):
        event_bus = Mock()
        tickets = {'tickets': {"responses": [{"ticketID": 3521039}]}}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200028729'}],
                          "ticketNotes": [{"noteValue": '{"#*Automaton Engine*#":""}'}]}}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        rpc_returns = [tickets, ticket_details, edge_status, edge_event, append_ticket]
        event_bus.rpc_request = CoroutineMock(side_effect=rpc_returns)
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._compose_ticket_note_object = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._compose_ticket_note_object.called is False

    @pytest.mark.asyncio
    async def poll_tickets_ko_wrong_serial_test(self):
        event_bus = Mock()
        tickets = {'tickets': {"responses": [{"ticketID": 3521039}]}}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'test'}],
                          "ticketNotes": [{"noteValue": '{"#*Automaton Engine*#":""}'}]}}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        rpc_returns = [tickets, ticket_details, edge_status, edge_event, append_ticket]
        event_bus.rpc_request = CoroutineMock(side_effect=rpc_returns)
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._compose_ticket_note_object = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._compose_ticket_note_object.called is False

    def find_recent_occurence_of_event_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
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
        edge_online_time = service_outage_triage._find_recent_occurence_of_event(event_list, 'EDGE_ALIVE')
        assert edge_online_time == '2019-07-30 06:38:00+00:00'
        link_online_time = service_outage_triage._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                                 'Link GE2 is no longer DEAD')
        assert link_online_time == '2019-07-30 4:26:00+00:00'
        link_dead_time = service_outage_triage._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                               'Link GE1 is no longer DEAD')
        assert link_dead_time is None

    def compose_ticket_note_object(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._find_recent_occurence_of_event = Mock()
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

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] == "GE1"
        assert ticket_object['Interface LABELMARK3'] == "GE2"
        assert ticket_object['Label LABELMARK2'] == "Test1"
        assert ticket_object['Label LABELMARK4'] == "Test2"
        assert service_outage_triage._find_recent_occurence_of_event.called

    def compose_ticket_note_one_links_GE1_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._find_recent_occurence_of_event = Mock()

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

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] == "GE1"
        assert ticket_object['Interface LABELMARK3'] is None
        assert ticket_object['Label LABELMARK2'] == "Test1"
        assert ticket_object['Label LABELMARK4'] is None
        assert service_outage_triage._find_recent_occurence_of_event.called

    def compose_ticket_note_one_links_GE2_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._find_recent_occurence_of_event = Mock()

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
                            "interface": "GE2",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        events_to_report = {'events': {'data': 'Some Event Info'}}

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] is None
        assert ticket_object['Interface LABELMARK3'] == "GE2"
        assert ticket_object['Label LABELMARK2'] is None
        assert ticket_object['Label LABELMARK4'] == "Test1"
        assert service_outage_triage._find_recent_occurence_of_event.called

    def compose_ticket_note_no_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._find_recent_occurence_of_event = Mock()

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

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] is None
        assert ticket_object['Interface LABELMARK3'] is None
        assert ticket_object['Label LABELMARK2'] is None
        assert ticket_object['Label LABELMARK4'] is None
        assert service_outage_triage._find_recent_occurence_of_event.called

    def compose_ticket_note_null_links_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._find_recent_occurence_of_event = Mock()

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

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] is None
        assert ticket_object['Interface LABELMARK3'] is None
        assert ticket_object['Label LABELMARK2'] is None
        assert ticket_object['Label LABELMARK4'] is None
        assert service_outage_triage._find_recent_occurence_of_event.called
