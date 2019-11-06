import json
from collections import OrderedDict
from datetime import datetime, timedelta
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions.service_outage_triage import ServiceOutageTriage
from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid

from application.actions import service_outage_triage as service_outage_triage_module
from config import testconfig


class TestServiceOutageTriage:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        assert service_outage_triage._event_bus is event_bus
        assert service_outage_triage._logger is logger
        assert service_outage_triage._scheduler is scheduler
        assert service_outage_triage._config is config

    @pytest.mark.asyncio
    async def start_service_outage_triage_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_triage_module, 'timezone', new=Mock()):
                await service_outage_triage.start_service_outage_triage_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_triage._poll_tickets, 'interval',
            minutes=config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_service_outage_triage_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_triage_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        await service_outage_triage.start_service_outage_triage_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_triage._poll_tickets, 'interval',
            minutes=config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=undefined,
            replace_existing=True,
            id='_service_outage_triage_process',
        )

    @pytest.mark.asyncio
    async def poll_tickets_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        tickets_list = []
        tickets = {'tickets': tickets_list}
        filtered_tickets_list = []

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=tickets)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=filtered_tickets_list)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            await service_outage_triage._poll_tickets()

        event_bus.rpc_request.assert_has_awaits([
            call('bruin.ticket.request',
                 json.dumps({
                     'request_id': uuid_,
                     'client_id': 85940,
                     'ticket_status': ['New', 'InProgress', 'Draft'],
                     'category': 'SD-WAN',
                     'ticket_topic': 'VOO'
                 }),
                 timeout=90, ),
            call('bruin.ticket.request',
                 json.dumps({
                     'request_id': uuid_,
                     'client_id': 9994,
                     'ticket_status': ['New', 'InProgress', 'Draft'],
                     'category': 'SD-WAN',
                     'ticket_topic': 'VOO'
                 }),
                 timeout=90, )
        ])
        service_outage_triage._filtered_ticket_details.assert_awaited_once_with(tickets)

    @pytest.mark.asyncio
    async def poll_tickets_with_bruin_tickets_returning_none_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        tickets = None

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=tickets)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._filtered_ticket_details = CoroutineMock()

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_side_effect = [uuid_1, uuid_2, uuid_3]
        with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
            await service_outage_triage._poll_tickets()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_1,
                    'client_id': 85940,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_2,
                    'client_id': 9994,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'notification.slack.request',
                json.dumps({
                    'request_id': uuid_3,
                    'message': (
                        f'Service outage triage: Error in ticket list. Ticket list: {json.dumps(tickets)}. '
                        'Environment: dev'
                    ),
                }),
                timeout=10,
            ),
        ])
        service_outage_triage._filtered_ticket_details.assert_not_awaited()
        logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def poll_tickets_with_bruin_tickets_json_missing_required_key_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        tickets = {'some-key-1': [], 'some-key-2': []}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=tickets)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._filtered_ticket_details = CoroutineMock()

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_side_effect = [uuid_1, uuid_2, uuid_3]
        with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
            await service_outage_triage._poll_tickets()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_1,
                    'client_id': 85940,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_2,
                    'client_id': 9994,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'notification.slack.request',
                json.dumps({
                    'request_id': uuid_3,
                    'message': (
                        f'Service outage triage: Error in ticket list. Ticket list: {json.dumps(tickets)}. '
                        'Environment: dev'
                    )
                }),
                timeout=10,
            ),
        ], any_order=False)
        service_outage_triage._filtered_ticket_details.assert_not_awaited()
        logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def poll_tickets_with_bruin_tickets_json_having_required_key_mapped_to_null_value_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        tickets_list = None
        tickets = {'tickets': tickets_list}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=tickets)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._filtered_ticket_details = CoroutineMock()

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_side_effect = [uuid_1, uuid_2, uuid_3]
        with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
            await service_outage_triage._poll_tickets()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_1,
                    'client_id': 85940,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'bruin.ticket.request',
                json.dumps({
                    'request_id': uuid_2,
                    'client_id': 9994,
                    'ticket_status': ['New', 'InProgress', 'Draft'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VOO'
                }),
                timeout=90,
            ),
            call(
                'notification.slack.request',
                json.dumps({
                    'request_id': uuid_3,
                    'message': (
                        f'Service outage triage: Error in ticket list. Ticket list: {json.dumps(tickets)}. '
                        'Environment: dev'
                    )
                }),
                timeout=10,
            ),
        ], any_order=False)
        service_outage_triage._filtered_ticket_details.assert_not_awaited()
        logger.error.assert_called_once()
    #
    # @pytest.mark.asyncio
    # async def poll_tickets_with_filtered_tickets_and_dev_environment_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     environment = 'dev'
    #     ticket_id = 3521039
    #
    #     ticket_details = {'ticketID': ticket_id}
    #     tickets_list = [ticket_details]
    #     tickets = {'tickets': tickets_list}
    #
    #     edge_id_by_serial = {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 958
    #     }
    #     edge_serial = 'VC05200026138'
    #     filtered_ticket_details = {'ticketID': ticket_id, 'serial': edge_serial}
    #     filtered_tickets_list = [filtered_ticket_details]
    #
    #     ticket_note_object = {"Ticket return object": "Ticket Note"}
    #     ticket_note_as_email_object = {'email_object': "Something happened"}
    #
    #     edge_status = {
    #         'edge_id': 'edge-123',
    #         'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
    #     }
    #     edge_event = {'edge_events': 'Some event info'}
    #     append_ticket = {'ticket_appended': 'Success'}
    #     send_to_slack = {'slack_sent': 'Success'}
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(side_effect=[
    #         tickets, edge_status, edge_event,
    #         append_ticket, send_to_slack
    #     ])
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #     service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=filtered_tickets_list)
    #     service_outage_triage._compose_ticket_note_object = Mock(return_value=ticket_note_object)
    #     service_outage_triage._template_renderer._ticket_object_to_email_obj =\
    #         Mock(return_value=ticket_note_as_email_object)
    #
    #     uuid_1 = uuid()
    #     uuid_2 = uuid()
    #     uuid_3 = uuid()
    #     uuid_4 = uuid()
    #     uuid_5 = uuid()
    #     uuid_side_effect = [uuid_3, uuid_4, uuid_5]
    #
    #     current_datetime = datetime.now()
    #     current_datetime_previous_week = current_datetime - timedelta(days=7)
    #     datetime_mock = Mock()
    #     datetime_mock.now = Mock(return_value=current_datetime)
    #
    #     custom_triage_config = config.TRIAGE_CONFIG.copy()
    #     custom_triage_config['environment'] = environment
    #     with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
    #         with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
    #             with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
    #                 await service_outage_triage._poll_tickets()
    #
    #     event_bus.rpc_request.assert_has_awaits([
    #         call(
    #             'bruin.ticket.request',
    #             json.dumps({
    #                 'request_id': uuid_1,
    #                 'client_id': 85940,
    #                 'ticket_status': ['New', 'InProgress', 'Draft'],
    #                 'category': 'SD-WAN',
    #                 'ticket_topic': 'VOO'
    #             }),
    #             timeout=90,
    #         ),
    #         call(
    #             'bruin.ticket.request',
    #             json.dumps({
    #                 'request_id': uuid_2,
    #                 'client_id': 9994,
    #                 'ticket_status': ['New', 'InProgress', 'Draft'],
    #                 'category': 'SD-WAN',
    #                 'ticket_topic': 'VOO'
    #             }),
    #             timeout=90,
    #         ),
    #         call(
    #             'edge.status.request',
    #             json.dumps({
    #                 'request_id': uuid_3,
    #                 'edge': edge_id_by_serial,
    #             }),
    #             timeout=10,
    #         ),
    #         call(
    #             'alert.request.event.edge',
    #             json.dumps({
    #                 'request_id': uuid_4,
    #                 'edge': edge_id_by_serial,
    #                 'start_date': current_datetime_previous_week,
    #                 'end_date': current_datetime,
    #                 'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
    #             }, default=str),
    #             timeout=180,
    #         ),
    #         call(
    #             'notification.email.request',
    #             json.dumps(ticket_note_as_email_object),
    #             timeout=10,
    #         ),
    #         call(
    #             'notification.slack.request',
    #             json.dumps({
    #                 'request_id': uuid_5,
    #                 'message': (
    #                     'Triage appended to ticket: '
    #                     f'https://app.bruin.com/helpdesk?clientId=85940&ticketId={ticket_id}, in {environment}'
    #                 )
    #             }),
    #             timeout=10,
    #         ),
    #     ], any_order=False)
    #     service_outage_triage._filtered_ticket_details.assert_awaited_once_with(tickets)
    #     service_outage_triage._compose_ticket_note_object.assert_called_once_with(edge_status, edge_event)
    #     service_outage_triage._template_renderer._ticket_object_to_email_obj.assert_called_once_with(ticket_note_object)
    #
    # @pytest.mark.asyncio
    # async def poll_tickets_with_filtered_tickets_and_production_environment_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     environment = 'production'
    #     ticket_id = 3521039
    #
    #     ticket_details = {'ticketID': ticket_id}
    #     tickets_list = [ticket_details]
    #     tickets = {'tickets': tickets_list}
    #
    #     edge_id_by_serial = {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 958
    #     }
    #     edge_serial = 'VC05200026138'
    #     filtered_ticket_details = {'ticketID': ticket_id, 'serial': edge_serial}
    #     filtered_tickets_list = [filtered_ticket_details]
    #
    #     ticket_note_object = {"Ticket return object": "Ticket Note"}
    #     ticket_note_as_string = "Something happened"
    #
    #     edge_status = {
    #         'edge_id': 'edge-123',
    #         'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
    #     }
    #     edge_event = {'edge_events': 'Some event info'}
    #     append_ticket = {'ticket_appended': 'Success'}
    #     send_to_slack = {'slack_sent': 'Success'}
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(side_effect=[
    #         tickets, edge_status, edge_event,
    #         append_ticket, send_to_slack
    #     ])
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #     service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=filtered_tickets_list)
    #     service_outage_triage._compose_ticket_note_object = Mock(return_value=ticket_note_object)
    #     service_outage_triage._ticket_object_to_string = Mock(return_value=ticket_note_as_string)
    #
    #     uuid_1 = uuid()
    #     uuid_2 = uuid()
    #     uuid_3 = uuid()
    #     uuid_4 = uuid()
    #     uuid_5 = uuid()
    #     uuid_6 = uuid()
    #     uuid_side_effect = [uuid_1, uuid_2, uuid_3, uuid_4, uuid_5, uuid_6]
    #
    #     current_datetime = datetime.now()
    #     current_datetime_previous_week = current_datetime - timedelta(days=7)
    #     datetime_mock = Mock()
    #     datetime_mock.now = Mock(return_value=current_datetime)
    #
    #     custom_triage_config = config.TRIAGE_CONFIG.copy()
    #     custom_triage_config['environment'] = environment
    #     with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
    #         with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
    #             with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
    #                 await service_outage_triage._poll_tickets()
    #
    #     event_bus.rpc_request.assert_has_awaits([
    #         call(
    #             'bruin.ticket.request',
    #             json.dumps({
    #                 'request_id': uuid_1,
    #                 'client_id': 85940,
    #                 'ticket_status': ['New', 'InProgress', 'Draft'],
    #                 'category': 'SD-WAN',
    #                 'ticket_topic': 'VOO'
    #             }),
    #             timeout=90,
    #         ),
    #         call(
    #             'bruin.ticket.request',
    #             json.dumps({
    #                 'request_id': uuid_2,
    #                 'client_id': 9994,
    #                 'ticket_status': ['New', 'InProgress', 'Draft'],
    #                 'category': 'SD-WAN',
    #                 'ticket_topic': 'VOO'
    #             }),
    #             timeout=90,
    #         ),
    #         call(
    #             'edge.status.request',
    #             json.dumps({
    #                 'request_id': uuid_3,
    #                 'edge': edge_id_by_serial,
    #             }),
    #             timeout=10,
    #         ),
    #         call(
    #             'alert.request.event.edge',
    #             json.dumps({
    #                 'request_id': uuid_4,
    #                 'edge': edge_id_by_serial,
    #                 'start_date': current_datetime_previous_week,
    #                 'end_date': current_datetime,
    #                 'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
    #             }, default=str),
    #             timeout=180,
    #         ),
    #         call(
    #             'bruin.ticket.note.append.request',
    #             json.dumps({
    #                 'request_id': uuid_5,
    #                 'ticket_id': ticket_id,
    #                 'note': ticket_note_as_string,
    #             }),
    #             timeout=15,
    #         ),
    #         call(
    #             'notification.slack.request',
    #             json.dumps({
    #                 'request_id': uuid_6,
    #                 'message': (
    #                     'Triage appended to ticket: '
    #                     f'https://app.bruin.com/helpdesk?clientId=85940&ticketId={ticket_id}, in {environment}'
    #                 )
    #             }),
    #             timeout=10,
    #         ),
    #     ], any_order=False)
    #     service_outage_triage._filtered_ticket_details.assert_awaited_once_with(tickets)
    #     service_outage_triage._compose_ticket_note_object.assert_called_once_with(edge_status, edge_event)
    #     service_outage_triage._ticket_object_to_string.assert_called_once_with(ticket_note_object)

    # @pytest.mark.asyncio
    # async def poll_tickets_with_filtered_tickets_and_unknown_environment_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     environment = None
    #     ticket_id = 3521039
    #
    #     ticket_details = {'ticketID': ticket_id}
    #     tickets_list = [ticket_details]
    #     tickets = {'tickets': tickets_list}
    #
    #     edge_serial = 'VC05200026138'
    #     filtered_ticket_details = {'ticketID': ticket_id, 'serial': edge_serial}
    #     filtered_tickets_list = [filtered_ticket_details]
    #
    #     edge_status = {
    #         'edge_id': 'edge-123',
    #         'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
    #     }
    #     edge_event = {'edge_events': 'Some event info'}
    #     append_ticket = {'ticket_appended': 'Success'}
    #     send_to_slack = {'slack_sent': 'Success'}
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(side_effect=[
    #         tickets, edge_status, edge_event,
    #         append_ticket, send_to_slack
    #     ])
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #     service_outage_triage._filtered_ticket_details = CoroutineMock(return_value=filtered_tickets_list)
    #     service_outage_triage._compose_ticket_note_object = Mock()
    #     service_outage_triage._ticket_object_to_string = Mock()
    #     service_outage_triage._template_renderer._ticket_object_to_email_obj = Mock()
    #
    #     custom_triage_config = config.TRIAGE_CONFIG.copy()
    #     custom_triage_config['environment'] = environment
    #     with patch.dict(config.TRIAGE_CONFIG, custom_triage_config, template_renderer):
    #         await service_outage_triage._poll_tickets()
    #
    #     service_outage_triage._filtered_ticket_details.assert_awaited_once_with(tickets)
    #     service_outage_triage._compose_ticket_note_object.assert_called_once_with(edge_status, edge_event)
    #     service_outage_triage._ticket_object_to_string.assert_not_called()
    #     service_outage_triage._template_renderer._ticket_object_to_email_obj.assert_not_called()

    @pytest.mark.asyncio
    async def filtered_ticket_details_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        tickets_list = []
        tickets = {'tickets': tickets_list}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_not_awaited()
        assert filtered_tickets == []

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_no_detailvalue_key_in_ticket_details_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        ticket_id = 3521039

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"some-key": 'some-value'}],
                "ticketNotes": [
                    {"noteValue": 'test info', 'createdDate': '2019-09-10 10:34:00-04:00'}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        assert filtered_tickets == []

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_existing_details_and_invalid_serial_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        ticket_id = 3521039
        invalid_serial = 'VC12345678912'

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": invalid_serial}],
                "ticketNotes": [
                    {"noteValue": 'test info', 'createdDate': '2019-09-10 10:34:00-04:00'}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        assert filtered_tickets == []

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_null_ticket_notes_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        ticket_id = 3521039
        edge_serial = 'VC05200026138'
        ticket_notes = None

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": edge_serial}],
                "ticketNotes": [
                    {"noteValue": ticket_notes, 'createdDate': '2019-09-10 10:34:00-04:00'}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        assert filtered_tickets == [{'ticketID': ticket_id, 'serial': edge_serial}]

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_no_existing_triage_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        ticket_id = 3521039
        edge_serial = 'VC05200026138'
        ticket_notes = 'test info'

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": edge_serial}],
                "ticketNotes": [
                    {"noteValue": ticket_notes, 'createdDate': '2019-09-10 10:34:00-04:00'}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        assert filtered_tickets == [{'ticketID': ticket_id, 'serial': edge_serial}]

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_existing_triage_and_no_timestamp_for_ticket_notes_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        ticket_id = 3521039
        edge_serial = 'VC05200026138'
        ticket_notes = '#*Automation Engine*#'

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": edge_serial}],
                "ticketNotes": [
                    {"noteValue": ticket_notes, 'createdDate': '2019-09-10 10:34:00-04:00'}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        assert filtered_tickets == []

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_existing_triage_and_timestamp_diff_lower_than_30_minutes_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        current_timestamp = '2019-09-10 10:45:00'
        ticket_notes_timestamp = '2019-09-10 10:34:00-04:00'
        ticket_notes_timestamp_naive = '2019-09-10 10:34:00'

        ticket_id = 3521039
        edge_serial = 'VC05200026138'
        ticket_notes = f'#*Automation Engine*# \n TimeStamp: {ticket_notes_timestamp}'

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": edge_serial}],
                "ticketNotes": [
                    {"noteValue": ticket_notes, 'createdDate': ticket_notes_timestamp}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._extract_field_from_string = Mock(return_value=ticket_notes_timestamp_naive)
        service_outage_triage._check_for_new_events = CoroutineMock()

        current_datetime = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
                filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        service_outage_triage._extract_field_from_string.assert_called_once_with(
            ticket_notes, 'TimeStamp: '
        )
        service_outage_triage._check_for_new_events.assert_not_awaited()
        assert filtered_tickets == []

    @pytest.mark.asyncio
    async def filtered_ticket_details_with_existing_triage_and_timestamp_diff_greater_than_30_minutes_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        current_timestamp = '2019-09-10 11:05:00'
        ticket_notes_timestamp = '2019-09-10 10:34:00-04:00'
        ticket_notes_timestamp_naive = '2019-09-10 10:34:00'

        ticket_id = 3521039
        edge_serial = 'VC05200026138'
        ticket_notes = f'#*Automation Engine*# \n TimeStamp: {ticket_notes_timestamp}'

        ticket_details = {'ticketID': ticket_id}
        tickets_list = [ticket_details]
        tickets = {'tickets': tickets_list}

        ticket_details = {
            'ticket_details': {
                "ticketDetails": [{"detailValue": edge_serial}],
                "ticketNotes": [
                    {"noteValue": ticket_notes, 'createdDate': ticket_notes_timestamp}
                ]
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=ticket_details)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._extract_field_from_string = Mock(return_value=ticket_notes_timestamp_naive)
        service_outage_triage._check_for_new_events = CoroutineMock()

        current_datetime = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        uuid_ = uuid()
        with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
            with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
                filtered_tickets = await service_outage_triage._filtered_ticket_details(tickets)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.details.request',
            json.dumps({
                'request_id': uuid_,
                'ticket_id': ticket_id,
            }),
            timeout=15,
        )
        service_outage_triage._extract_field_from_string.assert_called_once_with(
            ticket_notes, 'TimeStamp: '
        )
        service_outage_triage._check_for_new_events.assert_awaited_once_with(
            ticket_notes_timestamp_naive,
            {'ticketID': ticket_id, 'serial': edge_serial},
        )
        assert filtered_tickets == []

    def find_recent_occurence_of_event_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        event_list = [
            {
                'event': 'EDGE_ALIVE',
                'eventTime': '2019-07-30 06:38:00+00:00',
                'message': 'Edge is back up'
            },
            {
                'event': 'LINK_ALIVE',
                'eventTime': '2019-07-30 4:26:00+00:00',
                'message': 'Link GE2 is no longer DEAD'
            },
            {
                'event': 'EDGE_ALIVE',
                'eventTime': '2019-07-29 06:38:00+00:00',
                'message': 'Edge is back up'
            }
        ]

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

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
        template_renderer = Mock()
        dict_as_string = 'Edge Name: Test \nTimeStamp1: 2019-08-29 14:36:19-04:00 \nTimeStamp2 : Now \n'

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        timestamp = service_outage_triage._extract_field_from_string(dict_as_string, 'TimeStamp1: ', '\nTimeStamp2')

        assert timestamp == '2019-08-29 14:36:19-04:00 '
    #
    # @pytest.mark.asyncio
    # async def check_for_new_events_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     timestamp = '2019-07-30 00:26:00-04:00'
    #     ticket = {"ticketID": 123, "serial": "VC05200026138"}
    #     events_to_report = {
    #         'events': []
    #     }
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(return_value=events_to_report)
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #
    #     current_datetime = datetime.now()
    #     datetime_mock = Mock()
    #     datetime_mock.now = Mock(return_value=current_datetime)
    #
    #     uuid_ = uuid()
    #     with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
    #         with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
    #             await service_outage_triage._check_for_new_events(timestamp, ticket)
    #
    #     event_bus.rpc_request.assert_awaited_once_with(
    #         'alert.request.event.edge',
    #         json.dumps({
    #             'request_id': uuid_,
    #             'edge': {
    #                 "host": "mettel.velocloud.net",
    #                 "enterprise_id": 137,
    #                 "edge_id": 958
    #             },
    #             'start_date': timestamp,
    #             'end_date': current_datetime,
    #             'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
    #         }, default=str),
    #         timeout=180,
    #     )

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_check_they_are_sorted_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data]
        events_data_sorted_by_timestamp = [event_2_data, event_3_data, event_1_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 1500

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_any_call(events_data_sorted_by_timestamp)

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_event_note_less_than_event_limit_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 500

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data)
        ], any_order=False)

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_event_note_more_than_event_limit_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        config.TRIAGE_CONFIG['event_limit'] = 2
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 1500

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data]),
            call([event_2_data]),
            call([event_3_data]),
        ], any_order=False)

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_event_note_having_between_2k_and_3k_chars_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_4_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 09:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data, event_4_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 2500

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
        ], any_order=False)

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_event_note_having_more_than_3k_chars_no_reminder_test(
            self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_4_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 09:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_5_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 10:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_6_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 11:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data, event_4_data, event_5_data, event_6_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 3000

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data, event_3_data]),
            call([event_4_data, event_5_data, event_6_data]),
        ], any_order=False)

        event_7_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 12:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_8_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 13:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [
            event_1_data, event_2_data, event_3_data, event_4_data,
            event_5_data, event_6_data, event_7_data, event_8_data,
        ]
        events_to_report = {'events': events_data}
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        event_note = 'X' * 4000
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
            call([event_5_data, event_6_data]),
            call([event_7_data, event_8_data]),
        ], any_order=False)

        event_9_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 14:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_10_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 15:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [
            event_1_data, event_2_data, event_3_data, event_4_data,
            event_5_data, event_6_data, event_7_data, event_8_data,
            event_9_data, event_10_data,
        ]
        events_to_report = {'events': events_data}
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        event_note = 'X' * 5000
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
            call([event_5_data, event_6_data]),
            call([event_7_data, event_8_data]),
            call([event_9_data, event_10_data]),
        ], any_order=False)

    @pytest.mark.asyncio
    async def check_for_new_events_with_meaningful_events_and_event_note_having_more_than_3k_chars_reminder_test(
            self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        timestamp = '2019-07-30 00:26:00-04:00'
        ticket = {"ticketID": 123, "serial": "VC05200026138"}

        event_1_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 06:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_2_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_3_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 08:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_4_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 09:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_5_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 10:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_6_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 11:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [event_1_data, event_2_data, event_3_data, event_4_data, event_5_data, event_6_data]
        events_to_report = {'events': events_data}

        event_note = 'X' * 3001

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
            call([event_5_data, event_6_data]),
        ], any_order=False)

        event_7_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 12:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_8_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 13:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [
            event_1_data, event_2_data, event_3_data, event_4_data,
            event_5_data, event_6_data, event_7_data, event_8_data,
        ]
        events_to_report = {'events': events_data}
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        event_note = 'X' * 4001
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
            call([event_5_data, event_6_data]),
            call([event_7_data, event_8_data]),
        ], any_order=False)

        event_9_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 14:38:00+00:00',
            'message': 'GE2 alive'
        }
        event_10_data = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 15:38:00+00:00',
            'message': 'GE2 alive'
        }
        events_data = [
            event_1_data, event_2_data, event_3_data, event_4_data,
            event_5_data, event_6_data, event_7_data, event_8_data,
            event_9_data, event_10_data,
        ]
        events_to_report = {'events': events_data}
        event_bus.rpc_request = CoroutineMock(return_value=events_to_report)

        event_note = 'X' * 5001
        service_outage_triage._compose_event_note_object = Mock(return_value=event_note)

        await service_outage_triage._check_for_new_events(timestamp, ticket)

        service_outage_triage._compose_event_note_object.assert_has_calls([
            call(events_data),
            call([event_1_data, event_2_data]),
            call([event_3_data, event_4_data]),
            call([event_5_data, event_6_data]),
            call([event_7_data, event_8_data]),
            call([event_9_data, event_10_data]),
        ], any_order=False)
    #
    # @pytest.mark.asyncio
    # async def check_for_new_events_with_meaningful_events_and_production_environment_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     environment = 'production'
    #
    #     timestamp = '2019-07-30 00:26:00-04:00'
    #     ticket_id = 123
    #     ticket = {"ticketID": ticket_id, "serial": "VC05200026138"}
    #
    #     event_1_timestamp = '2019-07-30 06:38:00+00:00'
    #     event_2_timestamp = '2019-07-30 07:38:00+00:00'
    #     event_1_data = {
    #         'event': 'LINK_ALIVE',
    #         'category': 'NETWORK',
    #         'eventTime': event_1_timestamp,
    #         'message': 'GE2 alive'
    #     }
    #     event_2_data = {
    #         'event': 'LINK_ALIVE',
    #         'category': 'NETWORK',
    #         'eventTime': event_2_timestamp,
    #         'message': 'GE2 alive'
    #     }
    #     events_data = [event_1_data, event_2_data]
    #     events_to_report = {'events': events_data}
    #
    #     events_note = 'This is the note for all these events\n'
    #     events_note_timestamp = parse(event_2_timestamp).astimezone(timezone('US/Eastern')) + timedelta(seconds=1)
    #     events_ticket_note = f'#*Automation Engine*#{events_note}TimeStamp: {events_note_timestamp}'
    #
    #     rpc_response_append_ticket = rpc_response_slack_msg = None
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(side_effect=[
    #         events_to_report,
    #         rpc_response_append_ticket, rpc_response_slack_msg,
    #         rpc_response_append_ticket, rpc_response_slack_msg,
    #     ])
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #     service_outage_triage._compose_event_note_object = Mock(side_effect=[
    #         events_note, events_note
    #     ])
    #
    #     current_datetime = datetime.now()
    #     datetime_mock = Mock()
    #     datetime_mock.now = Mock(return_value=current_datetime)
    #
    #     uuid_1 = uuid()
    #     uuid_2 = uuid()
    #     uuid_3 = uuid()
    #     uuid_side_effect = [uuid_1, uuid_2, uuid_3]
    #
    #     custom_triage_config = config.TRIAGE_CONFIG.copy()
    #     custom_triage_config['environment'] = environment
    #     with patch.object(service_outage_triage_module, 'uuid', side_effect=uuid_side_effect):
    #         with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
    #             with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
    #                 await service_outage_triage._check_for_new_events(timestamp, ticket)
    #
    #     service_outage_triage._compose_event_note_object.assert_has_calls([
    #         call(events_data),
    #         call(events_data),
    #     ])
    #     event_bus.rpc_request.assert_has_awaits([
    #         call(
    #             'alert.request.event.edge',
    #             json.dumps({
    #                 'request_id': uuid_1,
    #                 'edge': {
    #                     "host": "mettel.velocloud.net",
    #                     "enterprise_id": 137,
    #                     "edge_id": 958
    #                 },
    #                 'start_date': timestamp,
    #                 'end_date': current_datetime,
    #                 'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
    #             }, default=str),
    #             timeout=180,
    #         ),
    #         call(
    #             'bruin.ticket.note.append.request',
    #             json.dumps({
    #                 'request_id': uuid_2,
    #                 'ticket_id': ticket_id,
    #                 'note': events_ticket_note,
    #             }),
    #             timeout=15,
    #         ),
    #         call(
    #             'notification.slack.request',
    #             json.dumps({
    #                 'request_id': uuid_3,
    #                 'message': (
    #                     'Events appended to ticket: https://app.bruin.com/helpdesk?clientId=85940&'
    #                     f'ticketId={ticket_id}, in production'
    #                 )
    #             }),
    #             timeout=10,
    #         ),
    #     ], any_order=False)
    #
    # @pytest.mark.asyncio
    # async def check_for_new_events_with_meaningful_events_and_unknown_environment_test(self):
    #     logger = Mock()
    #     scheduler = Mock()
    #     config = testconfig
    #     template_renderer = Mock()
    #
    #     environment = None
    #
    #     timestamp = '2019-07-30 00:26:00-04:00'
    #     ticket_id = 123
    #     ticket = {"ticketID": ticket_id, "serial": "VC05200026138"}
    #
    #     event_1_data = {
    #         'event': 'LINK_ALIVE',
    #         'category': 'NETWORK',
    #         'eventTime': '2019-07-30 06:38:00+00:00',
    #         'message': 'GE2 alive'
    #     }
    #     event_2_data = {
    #         'event': 'LINK_ALIVE',
    #         'category': 'NETWORK',
    #         'eventTime': '2019-07-30 07:38:00+00:00',
    #         'message': 'GE2 alive'
    #     }
    #     events_data = [event_1_data, event_2_data]
    #     events_to_report = {'events': events_data}
    #
    #     events_note = 'This is the note for all these events\n'
    #
    #     event_bus = Mock()
    #     event_bus.rpc_request = CoroutineMock(return_value=events_to_report)
    #
    #     service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
    #     service_outage_triage._compose_event_note_object = Mock(side_effect=[
    #         events_note, events_note
    #     ])
    #
    #     current_datetime = datetime.now()
    #     datetime_mock = Mock()
    #     datetime_mock.now = Mock(return_value=current_datetime)
    #
    #     uuid_ = uuid()
    #
    #     custom_triage_config = config.TRIAGE_CONFIG.copy()
    #     custom_triage_config['environment'] = environment
    #     with patch.object(service_outage_triage_module, 'uuid', return_value=uuid_):
    #         with patch.object(service_outage_triage_module, 'datetime', new=datetime_mock):
    #             with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
    #                 await service_outage_triage._check_for_new_events(timestamp, ticket)
    #
    #     service_outage_triage._compose_event_note_object.assert_has_calls([
    #         call(events_data),
    #         call(events_data),
    #     ])
    #     event_bus.rpc_request.assert_awaited_once_with(
    #         'alert.request.event.edge',
    #         json.dumps({
    #             'request_id': uuid_,
    #             'edge': {
    #                 "host": "mettel.velocloud.net",
    #                 "enterprise_id": 137,
    #                 "edge_id": 958
    #             },
    #             'start_date': timestamp,
    #             'end_date': current_datetime,
    #             'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
    #         }, default=str),
    #         timeout=180,
    #     )

    @pytest.mark.asyncio
    async def compose_event_note_object_edge_test(self):
        event_bus = Mock()

        events_to_report = [{'event': 'EDGE_UP', 'category': 'EDGE',
                             'eventTime': '2019-07-30 06:38:00+00:00',
                             'message': 'An Edge'}]
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        event_str = service_outage_triage._compose_event_note_object(events_to_report)

        assert 'Edge' in event_str

    @pytest.mark.asyncio
    async def compose_event_note_object_GE1_test(self):
        event_bus = Mock()

        events_to_report = [{'event': 'LINK_ALIVE', 'category': 'NETWORK',
                             'eventTime': '2019-07-30 06:38:00+00:00',
                             'message': 'GE1 alive'}]
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        event_str = service_outage_triage._compose_event_note_object(events_to_report)

        assert 'Interface GE1' in event_str

    @pytest.mark.asyncio
    async def compose_event_note_object_GE2_test(self):
        event_bus = Mock()

        events_to_report = [{'event': 'LINK_ALIVE', 'category': 'NETWORK',
                             'eventTime': '2019-07-30 06:38:00+00:00',
                             'message': 'GE2 alive'}]
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)

        event_str = service_outage_triage._compose_event_note_object(events_to_report)

        assert 'Interface GE2' in event_str

    def compose_ticket_note_object(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
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
        events_to_report = {'events': 'Some Event Info'}

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

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
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
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
        events_to_report = {'events': 'Some Event Info'}

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
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
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
        events_to_report = {'events': 'Some Event Info'}

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
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
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
        events_to_report = {'events': 'Some Event Info'}

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
        template_renderer = Mock()

        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
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
        events_to_report = {'events': 'Some Event Info'}

        ticket_object = service_outage_triage._compose_ticket_note_object(edges_to_report, events_to_report)

        assert isinstance(ticket_object, OrderedDict)
        assert ticket_object['Interface LABELMARK1'] is None
        assert ticket_object['Interface LABELMARK3'] is None
        assert ticket_object['Label LABELMARK2'] is None
        assert ticket_object['Label LABELMARK4'] is None
        assert service_outage_triage._find_recent_occurence_of_event.called

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        service_outage_triage = ServiceOutageTriage(event_bus, logger, scheduler, config, template_renderer)
        ticket_note = service_outage_triage._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'
