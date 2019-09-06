from collections import OrderedDict
from unittest.mock import Mock
import json
import pytest
from application.actions.service_outage_triage import ServiceOutageTriage
from apscheduler.util import undefined
from asynctest import CoroutineMock
from collections import OrderedDict

from config import testconfig


class TestServiceOutageTriage:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        assert isinstance(service_outage_triage, ServiceOutageTriage)
        assert service_outage_triage._event_bus is event_bus
        assert service_outage_triage._logger is logger
        assert service_outage_triage._scheduler is scheduler
        assert service_outage_triage._service_id == service_id
        assert service_outage_triage._config is config

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
        assert scheduler.add_job.call_args[1]['seconds'] == 120

    @pytest.mark.asyncio
    async def start_service_outage_triage_job_false_exec_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._poll_tickets = Mock()
        await service_outage_triage.start_service_outage_triage_job(exec_on_start=False)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is service_outage_triage._poll_tickets
        assert 'interval' in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == 120
        assert scheduler.add_job.call_args[1]['next_run_time'] == undefined

    @pytest.mark.asyncio
    async def poll_tickets_dev_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, edge_status, edge_event, append_ticket,
                                                           send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=[
            tickets['tickets'][0]])
        service_outage_triage._compose_ticket_note_object = Mock(return_value={"Ticket return object": "Ticket Note"})
        service_outage_triage._ticket_object_to_email_obj = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._filtered_ticket_details.called
        assert service_outage_triage._filtered_ticket_details.call_args[0][0] == tickets
        assert service_outage_triage._compose_ticket_note_object.called
        assert service_outage_triage._compose_ticket_note_object.call_args[0][0] == edge_status
        assert service_outage_triage._compose_ticket_note_object.call_args[0][1] == edge_event
        assert service_outage_triage._ticket_object_to_email_obj.called
        assert event_bus.rpc_request.mock_calls[3][1][0] == "notification.email.request"
        assert event_bus.rpc_request.mock_calls[3][1][1] == json.dumps("Ticket Note Object")

    @pytest.mark.asyncio
    async def poll_tickets_production_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, edge_status, edge_event, append_ticket,
                                                           send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'production'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=[
            tickets['tickets'][0]])
        service_outage_triage._compose_ticket_note_object = Mock(return_value={"Ticket return object": "Ticket Note"})
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._filtered_ticket_details.called
        assert service_outage_triage._filtered_ticket_details.call_args[0][0] == tickets
        assert service_outage_triage._compose_ticket_note_object.called
        assert service_outage_triage._compose_ticket_note_object.call_args[0][0] == edge_status
        assert service_outage_triage._compose_ticket_note_object.call_args[0][1] == edge_event
        assert service_outage_triage._ticket_object_to_string.called
        assert event_bus.rpc_request.mock_calls[3][1][0] == "bruin.ticket.note.append.request"
        assert 'note' in event_bus.rpc_request.mock_calls[3][1][1]

    @pytest.mark.asyncio
    async def poll_tickets_none_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        edge_status = {'edge_status': 'Some status info'}
        edge_event = {'edge_events': 'Some event info'}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, edge_status, edge_event, append_ticket,
                                                           send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = None
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=[
            tickets['tickets'][0]])
        service_outage_triage._compose_ticket_note_object = Mock(return_value={"Ticket return object": "Ticket Note"})
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")
        service_outage_triage._ticket_object_to_email_obj = Mock(return_value="Ticket Note Object")

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._filtered_ticket_details.called
        assert service_outage_triage._filtered_ticket_details.call_args[0][0] == tickets
        assert service_outage_triage._compose_ticket_note_object.called
        assert service_outage_triage._compose_ticket_note_object.call_args[0][0] == edge_status
        assert service_outage_triage._compose_ticket_note_object.call_args[0][1] == edge_event
        assert service_outage_triage._ticket_object_to_string.called is False
        assert service_outage_triage._ticket_object_to_email_obj.called is False
        assert event_bus.rpc_request.mock_calls[2][1][0] != "bruin.ticket.note.append.request"
        assert event_bus.rpc_request.mock_calls[2][1][0] != "notification.email.request"

    @pytest.mark.asyncio
    async def poll_tickets_none_bruin_ticket_response_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=None)
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = None
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._filtered_ticket_details = Mock()

        await service_outage_triage._poll_tickets()
        assert event_bus.rpc_request.called
        assert service_outage_triage._filtered_ticket_details.called is False
        assert logger.error.called is True

    @pytest.mark.asyncio
    async def filter_tickets_ok_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": 'test info'}]}}
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)
        assert event_bus.rpc_request.called
        assert filtered_tickets == [{"ticketID": 3521039, "serial": "VC05200026138"}]

    @pytest.mark.asyncio
    async def filter_tickets_ok_no_note_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": None}]}}
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)
        assert event_bus.rpc_request.called
        assert filtered_tickets == [{"ticketID": 3521039, "serial": "VC05200026138"}]

    @pytest.mark.asyncio
    async def filter_tickets_ko_no_detail_value_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{'detailId': '123'}],
                                             "ticketNotes": [{"noteValue": 'test info'}]}}
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)
        assert event_bus.rpc_request.called
        assert len(filtered_tickets) == 0

    @pytest.mark.asyncio
    async def filter_tickets_ko_wrong_detail_value_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": '123'}],
                                             "ticketNotes": [{"noteValue": 'test info'}]}}
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)
        assert event_bus.rpc_request.called
        assert len(filtered_tickets) == 0

    @pytest.mark.asyncio
    async def filter_tickets_ko_triage_exists_test(self):
        event_bus = Mock()
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200028729'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*#'}]}}
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._check_events = CoroutineMock()

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)
        assert event_bus.rpc_request.called
        assert len(filtered_tickets) == 0
        assert service_outage_triage._check_events.called
        assert service_outage_triage._check_events.call_args[0][1] == ticket_details['ticket_details']['ticketNotes'][
                                                                      0]['noteValue']

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
        assert json.dumps(edge_online_time, default=str) == json.dumps('2019-07-30 02:38:00-04:00')

        link_online_time = service_outage_triage._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                                 'Link GE2 is no longer DEAD')
        assert json.dumps(link_online_time, default=str) == json.dumps('2019-07-30 00:26:00-04:00')
        link_dead_time = service_outage_triage._find_recent_occurence_of_event(event_list, 'LINK_ALIVE',
                                                                               'Link GE1 is no longer DEAD')
        assert link_dead_time is None

    def extract_field_from_string_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123
        dict_as_string = 'Edge Name: Test \nTimeStamp1: 2019-08-29 14:36:19-04:00 \nTimeStamp2 : Now \n'
        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)

        timestamp = service_outage_triage._extract_field_from_string(dict_as_string, 'TimeStamp1: ', '\nTimeStamp2')

        assert timestamp == '2019-08-29 14:36:19-04:00 '

    @pytest.mark.asyncio
    async def check_events_dev_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'LINK_ALIVE', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE2 alive'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'dev'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert logger.info.called
        assert 'Ticket Note Object' in logger.info.call_args[0][0]
        assert service_outage_triage._ticket_object_to_string.called
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['NewEvent'] == 'LINK_ALIVE'
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['Device'] == 'Interface GE2'

    @pytest.mark.asyncio
    async def check_events_irrelevant_events_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'INTERFACE_UP', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE2 alive'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'dev'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert logger.info.called is False
        assert service_outage_triage._ticket_object_to_string.called is False

    @pytest.mark.asyncio
    async def check_events_no_timestamp_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'INTERFACE_UP', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE2 alive'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = ''
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'dev'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called is False
        assert logger.info.called is False
        assert service_outage_triage._ticket_object_to_string.called is False

    @pytest.mark.asyncio
    async def check_events_pro_edge_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'EDGE_UP', 'category': 'EDGE',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'An Edge'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'production'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert 'Ticket Note Object' in event_bus.rpc_request.mock_calls[1][1][1]
        assert service_outage_triage._ticket_object_to_string.called
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['NewEvent'] == 'EDGE_UP'
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['Device'] == 'Edge'

    @pytest.mark.asyncio
    async def check_events_pro_interface_GE1_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'LINK_DEAD', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE1 dead'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'production'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert 'Ticket Note Object' in event_bus.rpc_request.mock_calls[1][1][1]
        assert service_outage_triage._ticket_object_to_string.called
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['NewEvent'] == 'LINK_DEAD'
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['Device'] == 'Interface GE1'

    @pytest.mark.asyncio
    async def check_events_pro_interface_GE2_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'LINK_ALIVE', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE2 alive'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        logger.info = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'production'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert 'Ticket Note Object' in event_bus.rpc_request.mock_calls[1][1][1]
        assert service_outage_triage._ticket_object_to_string.called
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['NewEvent'] == 'LINK_ALIVE'
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['Device'] == 'Interface GE2'

    @pytest.mark.asyncio
    async def check_events_pro_interface_GE2_test(self):
        event_bus = Mock()

        events_to_report = {'events': {'data': [{'event': 'LINK_ALIVE', 'category': 'NETWORK',
                                                 'eventTime': '2019-07-30 06:38:00+00:00',
                                                 'message': 'GE2 alive'}]}}
        append_ticket = {'ticket_appeneded': 'Success'}
        send_to_slack = {'slack_sent': 'Success'}

        ticket_note = 'TimeStamp: 5 mins Ago \n'
        event_bus.rpc_request = CoroutineMock(side_effect=[events_to_report, append_ticket, send_to_slack])
        logger = Mock()
        logger.info = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['environment'] = 'production'
        service_id = 123

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        service_outage_triage._ticket_object_to_string = Mock(return_value="Ticket Note Object")

        await service_outage_triage._check_events(123, ticket_note)

        assert event_bus.rpc_request.called
        assert '5 mins Ago' in event_bus.rpc_request.mock_calls[0][1][1]
        assert 'Ticket Note Object' in event_bus.rpc_request.mock_calls[1][1][1]
        assert service_outage_triage._ticket_object_to_string.called
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['NewEvent'] == 'LINK_ALIVE'
        assert service_outage_triage._ticket_object_to_string.call_args[0][0]['Device'] == 'Interface GE2'

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

    def ticket_object_to_email_obj_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Company Events URL"] = 'test.com',
        ticket_dict['Events URL'] = 'event.com'
        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        email = service_outage_triage._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def ticket_object_to_email_obj_no_events_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        service_id = 123
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        email = service_outage_triage._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, service_id, config)
        ticket_note = service_outage_triage._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'
