from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions.tnba_feedback_action import TNBAFeedback
from application.actions import tnba_feedback_action as tnba_feedback_action_module
from config import testconfig


class TestTNBAMonitor:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        assert tnba_feedback._event_bus == event_bus
        assert tnba_feedback._logger == logger
        assert tnba_feedback._scheduler == scheduler
        assert tnba_feedback._config == config
        assert tnba_feedback._t7_repository == t7_repository
        assert tnba_feedback._customer_cache_repository == customer_cache_repository
        assert tnba_feedback._bruin_repository == bruin_repository
        assert tnba_feedback._notifications_repository == notifications_repository

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(tnba_feedback_action_module, 'datetime', new=datetime_mock):
            with patch.object(tnba_feedback_action_module, 'timezone', new=Mock()):
                await tnba_feedback.start_tnba_automated_process(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            tnba_feedback._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(tnba_feedback_action_module, 'datetime', new=datetime_mock):
            with patch.object(tnba_feedback_action_module, 'timezone', new=Mock()):
                await tnba_feedback.start_tnba_automated_process(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            tnba_feedback._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_job_id_already_started_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        try:
            await tnba_feedback.start_tnba_automated_process()
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                tnba_feedback._run_tickets_polling, 'interval',
                seconds=config.MONITORING_INTERVAL_SECONDS,
                next_run_time=undefined,
                replace_existing=False,
                id='_run_tickets_polling',
            )

    @pytest.mark.asyncio
    async def run_ticket_polling_test(self):
        ticket_ids_list = [456789, 432568, 43124]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)
        tnba_feedback._get_all_closed_tickets_for_monitored_companies = CoroutineMock(return_value=ticket_ids_list)
        tnba_feedback._send_ticket_task_history_to_t7 = CoroutineMock()

        await tnba_feedback._run_tickets_polling()

        tnba_feedback._get_all_closed_tickets_for_monitored_companies.assert_awaited_once()
        assert len(tnba_feedback._send_ticket_task_history_to_t7.call_args_list) == len(ticket_ids_list)

    @pytest.mark.asyncio
    async def get_all_closed_tickets_for_monitored_companies_test(self):
        customer_cache_response = {
            'body': [
                {
                    'edge': {
                        'host': 'mettel.velocloud.net',
                        'enterprise_id': 123,
                        'edge_id': 9999,
                    },
                    'last_contact': '2020-08-27T02:23:59',
                    'serial_number': 'VC1234567',
                    'bruin_client_info': {
                        'client_id': 9994,
                        'client_name': 'METTEL/NEW YORK',
                    },
                },
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_feedback_process = CoroutineMock(return_value=customer_cache_response)

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)
        tnba_feedback._get_closed_tickets_by_client_id = CoroutineMock()

        await tnba_feedback._get_all_closed_tickets_for_monitored_companies()
        customer_cache_repository.get_cache_for_feedback_process.assert_awaited_once()
        tnba_feedback._get_closed_tickets_by_client_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_all_closed_tickets_for_monitored_companies_with_customer_cache_still_building_test(self):
        customer_cache_response = {
            'body': 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net',
            'status': 202,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_feedback_process = CoroutineMock(return_value=customer_cache_response)

        redis_client = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository, redis_client)

        tnba_feedback._get_closed_tickets_by_client_id = CoroutineMock()

        await tnba_feedback._get_all_closed_tickets_for_monitored_companies()
        customer_cache_repository.get_cache_for_feedback_process.assert_awaited_once()
        tnba_feedback._get_closed_tickets_by_client_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_all_closed_tickets_for_monitored_companies_with_customer_cache_having_non_2xx_status_test(self):
        customer_cache_response = {
            'body': 'No edges were found for the specified filters',
            'status': 404,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_feedback_process = CoroutineMock(return_value=customer_cache_response)

        redis_client = Mock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository, redis_client)

        tnba_feedback._get_closed_tickets_by_client_id = CoroutineMock()

        await tnba_feedback._get_all_closed_tickets_for_monitored_companies()
        customer_cache_repository.get_cache_for_feedback_process.assert_awaited_once()
        tnba_feedback._get_closed_tickets_by_client_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_closed_tickets_by_client_id_test(self):
        closed_ticket_ids = []
        client_id = 85940
        outage_ticket_id = 123
        affecting_ticket_id = 321
        closed_outage_ticket_response = {
                                         'request_id': uuid(),
                                         'body': [{'clientID': client_id, 'ticketID': outage_ticket_id}],
                                         'status': 200
                                        }
        closed_affecting_ticket_response = {
                                             'request_id': uuid(),
                                             'body': [{'clientID': client_id, 'ticketID': affecting_ticket_id}],
                                             'status': 200
                                            }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_outage_tickets = CoroutineMock(return_value=closed_outage_ticket_response)
        bruin_repository.get_affecting_tickets = CoroutineMock(return_value=closed_affecting_ticket_response)

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)
        await tnba_feedback._get_closed_tickets_by_client_id(client_id, closed_ticket_ids)

        bruin_repository.get_outage_tickets.assert_awaited_with(client_id)
        bruin_repository.get_affecting_tickets.assert_awaited_with(client_id)
        assert closed_ticket_ids == [outage_ticket_id, affecting_ticket_id]

    @pytest.mark.asyncio
    async def get_closed_tickets_by_client_id_ticket_non_2xx_status_test(self):
        closed_ticket_ids = []
        client_id = 8594
        closed_outage_ticket_response = {
                                         'request_id': uuid(),
                                         'body': 'Error',
                                         'status': 400
                                        }
        closed_affecting_ticket_response = {
                                             'request_id': uuid(),
                                             'body': 'Error',
                                             'status': 400
                                            }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_outage_tickets = CoroutineMock(return_value=closed_outage_ticket_response)
        bruin_repository.get_affecting_tickets = CoroutineMock(return_value=closed_affecting_ticket_response)

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)
        await tnba_feedback._get_closed_tickets_by_client_id(client_id, closed_ticket_ids)

        bruin_repository.get_outage_tickets.assert_awaited_with(client_id)
        bruin_repository.get_affecting_tickets.assert_awaited_with(client_id)
        assert closed_ticket_ids == []

    @pytest.mark.asyncio
    async def get_closed_tickets_by_client_id_exception_test(self):
        closed_ticket_ids = []
        client_id = 8594
        closed_outage_ticket_response = {
            'request_id': uuid(),
            'body': 'Error',
            'status': 400
        }
        closed_affecting_ticket_response = {
            'request_id': uuid(),
            'body': 'Error',
            'status': 400
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_outage_tickets = CoroutineMock(side_effect=Exception)
        bruin_repository.get_affecting_tickets = CoroutineMock(return_value=closed_affecting_ticket_response)

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)
        await tnba_feedback._get_closed_tickets_by_client_id(client_id, closed_ticket_ids)

        bruin_repository.get_outage_tickets.assert_awaited_with(client_id)
        bruin_repository.get_affecting_tickets.assert_not_awaited()
        assert closed_ticket_ids == []

    @pytest.mark.asyncio
    async def send_ticket_task_history_to_t7_test(self):
        ticket_id = 123

        task_history = [{
                          "ClientName": "Le Duff Management ",
                          "Ticket Entered Date": "202008242225",
                          "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                          "CallTicketID": 4774915,
                          "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                          "DetailID": 5180688,
                          "Product": "SD-WAN",
                          "Asset": "VC05200030905",
                          "Address1": "1320 W Campbell Rd",
                          "Address2": None,
                          "City": "Richardson",
                          "State": "TX",
                          "Zip": "75080-2814",
                          "Site Name": "01106 Coit Campbell",
                          "NoteType": "ADN",
                          "Notes": "#*Automation Engine*#\nTNBA\n\n",
                          "Note Entered Date": "202008251726",
                          "EnteredDate_N": "2020-08-25T17:26:00.583-04:00",
                          "Note Entered By": "Intelygenz Ai",
                          "Task Assigned To": None,
                          "Task": None,
                          "Task Result": None,
                          "SLA": 1,
                          "Ticket Status": "Resolved"
                        }]

        # ticket_row = {"Asset": task_history[0]["Asset"],
        #               "Notes": task_history[0]["Notes"],
        #               "EnteredDate_N": task_history[0]["EnteredDate_N"],
        #               "Task Result": task_history[0]["Task Result"]}

        task_history_response = {
                                    "request_id": uuid(),
                                    "body": task_history,
                                    "status": 200
                                }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=task_history_response)

        t7_repository = Mock()
        t7_repository.tnba_note_in_task_history = Mock(return_value=True)
        t7_repository.post_metrics = CoroutineMock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        await tnba_feedback._send_ticket_task_history_to_t7(ticket_id)

        bruin_repository.get_ticket_task_history.assert_awaited_once()
        t7_repository.tnba_note_in_task_history.assert_called_once()
        t7_repository.post_metrics.assert_awaited_with(ticket_id, task_history)

    @pytest.mark.asyncio
    async def send_ticket_task_history_to_t7_task_history_return_non_2xx_test(self):
        ticket_id = 123

        task_history_response = {
                                    "request_id": uuid(),
                                    "body": "Failed",
                                    "status": 400
                                }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=task_history_response)

        t7_repository = Mock()
        t7_repository.tnba_note_in_task_history = Mock(return_value=True)
        t7_repository.post_metrics = CoroutineMock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        await tnba_feedback._send_ticket_task_history_to_t7(ticket_id)

        bruin_repository.get_ticket_task_history.assert_awaited_once()
        t7_repository.tnba_note_in_task_history.assert_not_called()
        t7_repository.post_metrics.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_ticket_task_history_to_t7_no_tnba_note_test(self):
        ticket_id = 123

        task_history = [{
                          "ClientName": "Le Duff Management ",
                          "Ticket Entered Date": "202008242225",
                          "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                          "CallTicketID": 4774915,
                          "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                          "DetailID": 5180688,
                          "Product": "SD-WAN",
                          "Asset": "VC05200030905",
                          "Address1": "1320 W Campbell Rd",
                          "Address2": None,
                          "City": "Richardson",
                          "State": "TX",
                          "Zip": "75080-2814",
                          "Site Name": "01106 Coit Campbell",
                          "NoteType": "ADN",
                          "Notes": "#*Automation Engine*#\n",
                          "Note Entered Date": "202008251726",
                          "EnteredDate_N": "2020-08-25T17:26:00.583-04:00",
                          "Note Entered By": "Intelygenz Ai",
                          "Task Assigned To": None,
                          "Task": None,
                          "Task Result": None,
                          "SLA": 1,
                          "Ticket Status": "Resolved"
                        }]

        ticket_row = {"Asset": task_history[0]["Asset"],
                      "Notes": task_history[0]["Notes"],
                      "EnteredDate_N": task_history[0]["EnteredDate_N"],
                      "Task Result": task_history[0]["Task Result"]}

        task_history_response = {
                                    "request_id": uuid(),
                                    "body": task_history,
                                    "status": 200
                                }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=task_history_response)

        t7_repository = Mock()
        t7_repository.tnba_note_in_task_history = Mock(return_value=False)
        t7_repository.post_metrics = CoroutineMock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        await tnba_feedback._send_ticket_task_history_to_t7(ticket_id)

        bruin_repository.get_ticket_task_history.assert_awaited_once()
        t7_repository.tnba_note_in_task_history.assert_called_once()
        t7_repository.post_metrics.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_ticket_task_history_to_t7_exception_test(self):
        ticket_id = 123

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(side_effect=Exception)

        t7_repository = Mock()
        t7_repository.tnba_note_in_task_history = Mock(return_value=False)
        t7_repository.post_metrics = CoroutineMock()

        tnba_feedback = TNBAFeedback(event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                                     bruin_repository, notifications_repository)

        await tnba_feedback._send_ticket_task_history_to_t7(ticket_id)

        bruin_repository.get_ticket_task_history.assert_awaited()
        t7_repository.tnba_note_in_task_history.assert_not_called()
        t7_repository.post_metrics.assert_not_awaited()
