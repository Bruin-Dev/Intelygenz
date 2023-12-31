import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime
from unittest.mock import ANY, AsyncMock, Mock, call, patch

import html2text
import pytest
from application.actions.repair_tickets_monitor import RepairTicketsMonitor, get_feedback_not_created_due_cancellations
from application.domain.asset import Topic
from application.domain.repair_email_output import CreateTicketsOutput, RepairEmailOutput, TicketOutput
from application.domain.ticket import Ticket, TicketStatus
from application.exceptions import ResponseException
from application.repositories.bruin_repository import BruinRepository
from application.rpc import RpcError
from application.rpc.upsert_outage_ticket_rpc import UpsertedStatus, UpsertedTicket
from config import testconfig as config
from framework.testing import case, given
from tests.fixtures.domain import AnyEmail, AnyEmailTag


@pytest.fixture(scope="module")
def inference_data_voo_validation_set(make_inference_data, make_filter_flags):
    return make_inference_data(
        predicted_class="VOO",
        potential_service_numbers=["VC12345"],
        potential_tickets_numbers=["654321"],
        filter_flags=make_filter_flags(in_validation_set=True),
    )


@pytest.fixture(scope="module")
def email_data_full_details(make_email):
    return make_email(
        email_id="12345",
        client_id="30000",
        received_date=datetime.utcnow(),
        subject="test subject",
        body="test body serial number: 56789",
        from_address="test@test.com",
        to_address=["address_1@test.com", "address_2@test.com"],
        send_cc=["test_cc@test.com", "test_cc2@test.com"],
    )


@pytest.fixture(scope="module")
def existing_ticket_data_voo_with_service_numbers(make_ticket_decamelized):
    ticket = make_ticket_decamelized(
        ticket_id="1234",
        client_id="30000",
        ticket_status="In Progress",
        call_type="",
        category="VOO",
        create_date=datetime.utcnow(),
        created_by="test bot",
    )
    ticket["service_numbers"] = ["1235", "4366"]
    ticket["site_id"] = "site_name"
    return ticket


@pytest.fixture(scope="module")
def ticket_note_previous_cancellation():
    return {
        "ticketNotes": [
            {
                "noteId": 93603255,
                "noteType": "CancellationReason",
                "noteValue": "becausecos I can do it!",
                "serviceNumber": ["VC05100049698"],
                "createdDate": "2022-02-08T17:06:08.083-05:00",
                "creator": "Intelygenz Bot",
            },
        ]
    }


@pytest.fixture(scope="module")
def resolved_ticket_data_with_cancellation(make_ticket_decamelized, ticket_note_previous_cancellation):
    ticket = make_ticket_decamelized(
        ticket_id="12345",
        client_id="30000",
        ticket_status="Resolved",
        call_type="",
        category="VOO",
        create_date=datetime.utcnow(),
        created_by="test bot",
    )
    ticket["service_numbers"] = ["1235"]
    ticket["site_id"] = "site_name_2"
    ticket["ticket_notes"] = ticket_note_previous_cancellation["ticketNotes"]
    return ticket


@pytest.fixture(scope="module")
def email_data_no_cc_details(make_email):
    return make_email(
        email_id="12345",
        client_id="30000",
        received_date=datetime.utcnow(),
        subject="test subject",
        body="test body serial number: 56789",
        from_address="test@test.com",
        to_address=["address_1@test.com", "address_2@test.com"],
    )


@pytest.fixture(scope="module")
def tag_data_repair():
    return {
        "tag_id": 1,
        "email_id": "12345",
    }


@pytest.fixture(scope="module")
def tag_data_new_order():
    return {
        "tag_id": 2,
        "email_id": "12345",
    }


class TestRepairTicketsMonitor:
    def instance_test(
        self,
        event_bus,
        scheduler,
        bruin_repository,
        new_tagged_emails_repository,
        repair_ticket_kre_repository,
    ):
        repair_tickets_monitor = RepairTicketsMonitor(
            event_bus,
            scheduler,
            config,
            bruin_repository,
            new_tagged_emails_repository,
            repair_ticket_kre_repository,
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
        )

        assert repair_tickets_monitor._event_bus == event_bus
        assert repair_tickets_monitor._scheduler == scheduler
        assert repair_tickets_monitor._config == config
        assert repair_tickets_monitor._bruin_repository == bruin_repository
        assert repair_tickets_monitor._new_tagged_emails_repository == new_tagged_emails_repository
        assert repair_tickets_monitor._repair_tickets_kre_repository == repair_ticket_kre_repository

    @pytest.mark.asyncio
    async def start_repair_tickets_monitor__exec_on_start_test(self, repair_tickets_monitor, scheduler):
        next_run_time = datetime.now()

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch("application.actions.repair_tickets_monitor.datetime", datetime_mock):
            await repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            repair_tickets_monitor._run_repair_tickets_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["repair_ticket_monitor"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_run_repair_tickets_polling",
        )

    def _triage_emails_by_tag_test(self, repair_tickets_monitor):
        tagged_emails = [
            AnyEmail(tag=AnyEmailTag(type="1")),
            AnyEmail(tag=AnyEmailTag(type="2")),
        ]

        repair_emails, other_emails = repair_tickets_monitor._triage_emails_by_tag(tagged_emails)

        assert list(repair_emails)[0] == tagged_emails[0]
        assert list(other_emails)[0] == tagged_emails[1]

    @pytest.mark.asyncio
    async def _get_parent_email_inference__ok_test(
        self,
        repair_tickets_monitor,
        inference_data_voo_validation_set,
        make_rpc_response,
    ):
        email = AnyEmail(date=datetime(2000, 1, 1), cc_addresses=["cc1", "cc2"])
        expected_cc = "cc1, cc2"
        rpc_response = make_rpc_response(status=200, body=inference_data_voo_validation_set)

        repair_tickets_kre_repository = AsyncMock()
        repair_tickets_kre_repository.get_email_inference = AsyncMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once_with(
            {
                "email_id": email.id,
                "client_id": email.client_id,
                "subject": email.subject,
                "body": email.body,
                "date": "2000-01-01T00:00:00",
                "from_address": email.sender_address,
                "to": email.recipient_addresses,
                "cc": expected_cc,
                "is_auto_reply_answer": False,
                "auto_reply_answer_delay": None,
            },
            {"tag_probability": email.tag.probability},
        )

        assert response == inference_data_voo_validation_set

    @pytest.mark.asyncio
    async def _get_reply_email_inference__ok_test(
        self,
        repair_tickets_monitor,
        inference_data_voo_validation_set,
        make_rpc_response,
    ):
        email = AnyEmail(
            date=datetime(2000, 1, 1, 0, 0, 10),
            cc_addresses=["cc1", "cc2"],
            parent=AnyEmail(date=datetime(2000, 1, 1, 0, 0, 0)),
        )
        expected_cc = "cc1, cc2"
        rpc_response = make_rpc_response(status=200, body=inference_data_voo_validation_set)

        repair_tickets_kre_repository = AsyncMock()
        repair_tickets_kre_repository.get_email_inference = AsyncMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once_with(
            {
                "email_id": email.id,
                "client_id": email.client_id,
                "subject": email.subject,
                "body": email.body,
                "date": "2000-01-01T00:00:10",
                "from_address": email.sender_address,
                "to": email.recipient_addresses,
                "cc": expected_cc,
                "is_auto_reply_answer": True,
                "auto_reply_answer_delay": 10,
            },
            {"tag_probability": email.tag.probability},
        )

        assert response == inference_data_voo_validation_set

    @pytest.mark.asyncio
    async def _get_inference__no_cc_test(
        self,
        repair_tickets_monitor,
        inference_data_voo_validation_set,
        make_rpc_response,
    ):
        email = AnyEmail(date=datetime(2000, 1, 1), cc_addresses=[])
        expected_cc = ""
        rpc_response = make_rpc_response(status=200, body=inference_data_voo_validation_set)

        repair_tickets_kre_repository = AsyncMock()
        repair_tickets_kre_repository.get_email_inference = AsyncMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once_with(
            {
                "email_id": email.id,
                "client_id": email.client_id,
                "subject": email.subject,
                "body": email.body,
                "date": "2000-01-01T00:00:00",
                "from_address": email.sender_address,
                "to": email.recipient_addresses,
                "cc": expected_cc,
                "is_auto_reply_answer": False,
                "auto_reply_answer_delay": None,
            },
            {"tag_probability": email.tag.probability},
        )

        assert response == inference_data_voo_validation_set

    @pytest.mark.asyncio
    async def _get_inference__not_200_test(
        self,
        repair_tickets_monitor,
        make_rpc_response,
    ):
        rpc_response = make_rpc_response(status=400, body="Error in data")
        repair_tickets_kre_repository = AsyncMock()
        repair_tickets_kre_repository.get_email_inference = AsyncMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(AnyEmail())

        assert response is None

    @pytest.mark.asyncio
    async def _save_outputs__ok_test(self, repair_tickets_monitor, make_rpc_response, make_rta_ticket_payload):
        rpc_response_200 = make_rpc_response(status=200, body={"success": True})
        tickets_created = make_rta_ticket_payload(ticket_id="5678", site_id="5678")

        response = Mock()
        response.data = json.dumps(rpc_response_200).encode()
        repair_tickets_monitor._repair_tickets_kre_repository._event_bus.request = AsyncMock(return_value=response)
        save_outputs_response = await repair_tickets_monitor._save_output(
            RepairEmailOutput(email_id=1234, service_numbers_sites_map={"1234": "5678"})
        )

        assert save_outputs_response == {"success": True}

    @pytest.mark.asyncio
    async def _save_outputs__not_200_test(self, repair_tickets_monitor, make_rpc_response):
        rpc_response_400 = make_rpc_response(status=400, body="Error")

        with patch.object(
            repair_tickets_monitor._repair_tickets_kre_repository._event_bus,
            "request",
            return_value=asyncio.Future(),
        ) as rpc_mock:
            rpc_mock.return_value.set_result(rpc_response_400)
            result = await repair_tickets_monitor._save_output(
                RepairEmailOutput(email_id=1234, service_numbers_sites_map={"1234": "5678"})
            )

        assert result is None

    def get_site_ids_with_previous_cancellations__test(
        self,
        repair_tickets_monitor,
        existing_ticket_data_voo_with_service_numbers,
        resolved_ticket_data_with_cancellation,
    ):
        """
        existing_tickets has site_ids ['site_name']
        resolved_tikets has ['site_name_2']
        Assert  [site_name_2]
        """
        site_id = repair_tickets_monitor.get_site_ids_with_previous_cancellations(
            [
                existing_ticket_data_voo_with_service_numbers,
                resolved_ticket_data_with_cancellation,
            ]
        )

        assert site_id == ["site_name_2"]

    def get_site_ids_with_previous_cancellations_empty_tickets__test(
        self,
        repair_tickets_monitor,
    ):
        site_id = repair_tickets_monitor.get_site_ids_with_previous_cancellations([])

        assert site_id == []

    def get_site_ids_with_previous_cancellations_no_cancellations__test(
        self,
        repair_tickets_monitor,
        existing_ticket_data_voo_with_service_numbers,
    ):
        """
        existing_tickets has site_ids ['site_name']
        Assert  []
        """
        site_id = repair_tickets_monitor.get_site_ids_with_previous_cancellations(
            [existing_ticket_data_voo_with_service_numbers]
        )

        assert site_id == []

    def get_service_number_site_id_map_with_and_without_cancellations_test(self, repair_tickets_monitor):
        service_numbers_site_id_map = {
            "12345": "site_name_1",
            "54321": "site_name_2",
            "11111": "site_name_2",
            "22222": "site_name_3",
        }
        site_ids_with_cancellations = ["site_name_2"]

        service_number_site_ids_without_cancellations = (
            repair_tickets_monitor.get_service_number_site_id_map_with_and_without_cancellations(
                service_numbers_site_id_map, site_ids_with_cancellations
            )
        )

        assert service_number_site_ids_without_cancellations == (
            {"54321": "site_name_2", "11111": "site_name_2"},
            {"12345": "site_name_1", "22222": "site_name_3"},
        )

    def get_services_numbers_site_id_map_without_cancellations_empty_cancellations__test(self, repair_tickets_monitor):
        service_numbers_site_id_map = {
            "12345": "site_name_1",
            "54321": "site_name_2",
            "11111": "site_name_2",
            "22222": "site_name_3",
        }
        site_ids_with_cancellations = []

        service_number_site_ids_without_cancellations = (
            repair_tickets_monitor.get_service_number_site_id_map_with_and_without_cancellations(
                service_numbers_site_id_map, site_ids_with_cancellations
            )
        )

        assert service_number_site_ids_without_cancellations == (
            defaultdict(None, {}),
            service_numbers_site_id_map,
        )

    def get_feedback_not_created_due_cancellations__test(self, repair_tickets_monitor):
        # {service_number: site_id}
        map_with_cancellations = {
            "123456": "site_name_1",
            "123457": "site_name_2",
            "123458": "site_name_1",
            "123459": "site_name_3",
        }

        feedback = get_feedback_not_created_due_cancellations(map_with_cancellations)

        assert feedback == [
            TicketOutput(
                site_id="site_name_1",
                service_numbers=["123456", "123458"],
                reason="A previous ticket on that site was recently cancelled",
            ),
            TicketOutput(
                site_id="site_name_2",
                service_numbers=["123457"],
                reason="A previous ticket on that site was recently cancelled",
            ),
            TicketOutput(
                site_id="site_name_3",
                service_numbers=["123459"],
                reason="A previous ticket on that site was recently cancelled",
            ),
        ]

    def get_feedback_not_created_due_cancellations_empty__test(self, repair_tickets_monitor):
        # {service_number: site_id}
        map_with_cancellations = {}

        feedback = get_feedback_not_created_due_cancellations(map_with_cancellations)

        assert feedback == []

    def get_services_numbers_site_id_map_without_cancellations_all_empty__test(self, repair_tickets_monitor):
        service_numbers_site_id_map = {}
        site_ids_with_cancellations = []

        service_number_site_ids_without_cancellations = (
            repair_tickets_monitor.get_service_number_site_id_map_with_and_without_cancellations(
                service_numbers_site_id_map, site_ids_with_cancellations
            )
        )

        assert service_number_site_ids_without_cancellations == (
            defaultdict(None, {}),
            defaultdict(None, {}),
        )

    @pytest.mark.asyncio
    async def _process_other_tags_email_test(self, repair_tickets_monitor, tag_data_new_order):
        email = AnyEmail(tag=AnyEmailTag(type="2"))
        repair_tickets_monitor._new_tagged_emails_repository = Mock()

        await repair_tickets_monitor._process_other_tags_email(email)

        repair_tickets_monitor._new_tagged_emails_repository.mark_complete.assert_called_once_with(email.id)

    @pytest.mark.asyncio
    async def _process_repair_email__ok_test(
        self,
        repair_tickets_monitor,
        make_inference_data,
        make_ticket_decamelized,
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        inference_data = make_inference_data()
        service_number_site_map = {
            "1234": "site_1",
            "2345": "site_2",
        }

        tickets_created = [TicketOutput(site_id="site_1", service_numbers=["1234"], ticket_id="5678")]
        tickets_updated = [TicketOutput(site_id="site_2", service_numbers=["2345"], ticket_id="1234")]

        create_ticket_response = CreateTicketsOutput(tickets_created=tickets_created, tickets_updated=tickets_updated)
        existing_tickets_response = [make_ticket_decamelized()]
        save_outputs_response = {"success": True}

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(return_value=service_number_site_map)
        repair_tickets_monitor._get_tickets = AsyncMock(return_value=[])
        repair_tickets_monitor._get_existing_tickets = AsyncMock(return_value=existing_tickets_response)
        repair_tickets_monitor._create_tickets = AsyncMock(return_value=create_ticket_response)
        repair_tickets_monitor._save_output = AsyncMock(return_value=save_outputs_response)
        repair_tickets_monitor._get_asset_topics_rpc = AsyncMock(return_value=[Topic(call_type="REP", category="VOO")])
        repair_tickets_monitor._bruin_repository.mark_email_as_done = AsyncMock()

        await repair_tickets_monitor._process_repair_email(email)

        repair_tickets_monitor._save_output.assert_awaited_once()
        new_tagged_emails_repository.mark_complete.assert_called_once_with(email_id)
        repair_tickets_monitor._bruin_repository.mark_email_as_done.assert_awaited_once_with(email_id)

    @pytest.mark.asyncio
    async def _process_repair_email__no_inference_data_test(self, repair_tickets_monitor):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        validated_tickes = {
            "validated_ticket_numbers": ["1234"],
            "bruin_ticket_status_map": [{"1234": "site_1"}],
            "bruin_ticket_call_type_map": [],
            "bruin_ticket_category_map": [],
        }

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository
        repair_tickets_monitor._get_tickets = AsyncMock(return_value=validated_tickes)
        repair_tickets_monitor._save_output = AsyncMock(return_value=None)
        repair_tickets_monitor._get_inference = AsyncMock(return_value=None)

        await repair_tickets_monitor._process_repair_email(email)
        repair_tickets_monitor._save_output.assert_not_awaited()

    @pytest.mark.asyncio
    async def _process_repair_email__ok__with_cancellations_test(
        self,
        repair_tickets_monitor,
        make_inference_data,
        existing_ticket_data_voo_with_service_numbers,
        resolved_ticket_data_with_cancellation,
        make_filter_flags,
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(potential_tickets_numbers=["1234"], filter_flags=filter_flags)
        service_number_site_map = {
            "1234": "site_name_1",
            "2345": "site_name_2",
        }

        tickets_created = [{"site_id": "site_name_1", "service_numbers": ["1234"], "ticket_id": "5678"}]
        tickets_updated = [{"site_id": "site_name_2", "service_numbers": ["2345"], "ticket_id": "1234"}]
        tickets_not_created = []
        validated_tickets = [
            Ticket(site_id="site_1", id="1234"),
            Ticket(site_id="site_1", id="1235"),
        ]
        active_tickets = []
        create_ticket_response = (tickets_created, tickets_updated, tickets_not_created)
        existing_tickets_response = [
            resolved_ticket_data_with_cancellation,
            existing_ticket_data_voo_with_service_numbers,
        ]
        save_outputs_response = {"success": True}

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(return_value=service_number_site_map)
        repair_tickets_monitor._get_tickets = AsyncMock(return_value=validated_tickets)
        repair_tickets_monitor._get_existing_tickets = AsyncMock(return_value=existing_tickets_response)
        repair_tickets_monitor._create_tickets = AsyncMock(return_value=create_ticket_response)
        repair_tickets_monitor._save_output = AsyncMock(return_value=save_outputs_response)
        repair_tickets_monitor._bruin_repository.mark_email_as_done = AsyncMock()
        repair_tickets_monitor._get_asset_topics_rpc = AsyncMock(return_value=[Topic(call_type="REP", category="VOO")])

        await repair_tickets_monitor._process_repair_email(email)

        repair_tickets_monitor._save_output.assert_awaited_once()
        # await_args[0] is args and await_args[1] is kwargs
        assert repair_tickets_monitor._save_output.await_args[0][0].tickets_cannot_be_created == [
            TicketOutput(
                site_id="site_name_2",
                service_numbers=["2345"],
                reason="A previous ticket on that site was recently cancelled",
            )
        ]
        assert repair_tickets_monitor._save_output.await_args[0][0].validated_tickets == [
            Ticket(site_id="site_1", id="1234"),
            Ticket(site_id="site_1", id="1235"),
        ]
        new_tagged_emails_repository.mark_complete.assert_called_once_with(email_id)
        repair_tickets_monitor._bruin_repository.mark_email_as_done.assert_not_awaited()

    @pytest.mark.asyncio
    async def _process_repair_email__site_map_error_test(
        self, repair_tickets_monitor, make_filter_flags, make_inference_data
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(potential_tickets_numbers=["1234"], filter_flags=filter_flags)

        response_exception = ResponseException("Error")
        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository
        repair_tickets_monitor._save_output = AsyncMock(return_value=None)
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(side_effect=response_exception)

        await repair_tickets_monitor._process_repair_email(email)
        repair_tickets_monitor._save_output.assert_awaited_once_with(
            RepairEmailOutput(
                email_id=email_id, tickets_cannot_be_created=[TicketOutput(reason=str(response_exception))]
            )
        )

    @pytest.mark.asyncio
    async def _process_repair_email__site_map_error_with_validated_tickets_test(
        self, repair_tickets_monitor, make_filter_flags, make_inference_data
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(potential_tickets_numbers=["1234"], filter_flags=filter_flags)

        response_exception = ResponseException("Error")
        repair_tickets_monitor._save_output = AsyncMock(return_value=None)
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(side_effect=response_exception)
        repair_tickets_monitor._bruin_repository.get_single_ticket_basic_info = AsyncMock(
            return_value={
                "status": 200,
                "body": {"ticket_id": "1234", "ticket_status": "InProgress", "call_type": "REP", "category": "VOO"},
            }
        )

        await repair_tickets_monitor._process_repair_email(email)
        repair_tickets_monitor._save_output.assert_awaited_once_with(
            RepairEmailOutput(
                email_id=email_id,
                tickets_cannot_be_created=[TicketOutput(reason=str(response_exception))],
                validated_tickets=[Ticket(id="1234", status=TicketStatus.IN_PROGRESS, call_type="REP", category="VOO")],
            )
        )

    @pytest.mark.asyncio
    async def _process_repair_email__not_actionable_predicted_other_test(
        self,
        repair_tickets_monitor,
        make_filter_flags,
        make_inference_data,
        make_ticket_decamelized,
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(
            potential_tickets_numbers=["1234"],
            filter_flags=filter_flags,
            predicted_class="Other",
        )
        service_number_site_map = {
            "1234": "site_name_1",
            "2345": "site_name_2",
        }
        create_tickets_output = CreateTicketsOutput(
            tickets_created=[TicketOutput(site_id="site_1", service_numbers=["1234"], ticket_id="5678")],
            tickets_updated=[TicketOutput(site_id="site_2", service_numbers=["2345"], ticket_id="1234")],
        )

        existing_tickets_response = [make_ticket_decamelized()]

        repair_tickets_monitor._save_output = AsyncMock(return_value=None)
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(return_value=service_number_site_map)
        repair_tickets_monitor._get_existing_tickets = AsyncMock(return_value=existing_tickets_response)
        repair_tickets_monitor._create_tickets = AsyncMock(return_value=create_tickets_output)
        repair_tickets_monitor._get_asset_topics_rpc = AsyncMock(return_value=[Topic(call_type="REP", category="VOO")])

        await repair_tickets_monitor._process_repair_email(email)

        assert (
            repair_tickets_monitor._save_output.call_args_list[0][0][0].tickets_cannot_be_created[0].reason
            == "predicted class is Other"
        )

    @pytest.mark.asyncio
    async def _get_valid_service_numbers_site_map__ok_test(self, repair_tickets_monitor, make_rpc_response):
        verified_service_number_body = {
            "client_id": "1234",
            "client_name": "client_name",
            "site_id": "5678",
        }
        verified_service_number_response = make_rpc_response(status=200, body=verified_service_number_body)

        bruin_repository = Mock()
        bruin_repository.verify_service_number_information = AsyncMock(return_value=verified_service_number_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        valid_service_numbers_site_map = await repair_tickets_monitor._get_valid_service_numbers_site_map(
            "1345", potential_service_numbers=["10111"]  # Client_id
        )

        assert valid_service_numbers_site_map == {"10111": "5678"}

    @pytest.mark.asyncio
    async def _get_valid_service_numbers_site_map__not_200_test(self, repair_tickets_monitor, make_rpc_response):
        client_id = "1234"
        potential_service_numbers = ["10111"]
        verified_service_number_response = make_rpc_response(status=400, body="Error message")

        repair_tickets_monitor._bruin_repository.verify_service_number_information = AsyncMock(
            return_value=verified_service_number_response
        )

        with pytest.raises(ResponseException):
            await repair_tickets_monitor._get_valid_service_numbers_site_map(client_id, potential_service_numbers)

    @pytest.mark.asyncio
    async def _get_valid_service_numbers_site_map__404_test(self, repair_tickets_monitor, make_rpc_response):
        verified_service_number_response = make_rpc_response(status=404, body="")
        repair_tickets_monitor._bruin_repository.verify_service_number_information = AsyncMock(
            return_value=verified_service_number_response
        )

        # No valid service numbers
        subject = await repair_tickets_monitor._get_valid_service_numbers_site_map(
            "1345", potential_service_numbers=["10111"]  # Client_id
        )

        assert subject == {}

    @pytest.mark.asyncio
    async def _get_existing_tickets__ok_test(
        self,
        repair_tickets_monitor,
        make_ticket,
        make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_ticket = make_ticket(client_id=client_id, ticket_id=1245)
        open_ticket["service_numbers"] = ["1234", "2345"]
        open_tickets_rpc_response = make_rpc_response(status=200, body=[open_ticket])

        expected_result = open_ticket.copy()
        expected_result["site_id"] = site_id
        expected_result = [expected_result]

        bruin_repository = Mock()
        bruin_repository.get_existing_tickets_with_service_numbers = AsyncMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        result = await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

        assert result == expected_result

    @pytest.mark.asyncio
    async def _get_existing_tickets__404_test(
        self,
        repair_tickets_monitor,
        make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_tickets_rpc_response = make_rpc_response(status=404, body=[])

        expected_result = []

        bruin_repository = Mock()
        bruin_repository.get_existing_tickets_with_service_numbers = AsyncMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        result = await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

        assert result == expected_result

    @pytest.mark.asyncio
    async def _get_existing_tickets__not_200_test(
        self,
        repair_tickets_monitor,
        make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_tickets_rpc_response = make_rpc_response(status=400, body=[])

        bruin_repository = Mock()
        bruin_repository.get_existing_tickets_with_service_numbers = AsyncMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        with pytest.raises(ResponseException):
            await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

    def _get_potential_tickets__could_be_updated_tickets_test(
        self,
        repair_tickets_monitor,
        make_filter_flags,
        make_inference_data,
        existing_ticket_data_voo_with_service_numbers,
    ):
        predicted_class = "VOO"
        filter_flags = make_filter_flags(in_validation_set=True)
        site_id = existing_ticket_data_voo_with_service_numbers["site_id"]
        existing_ticket = existing_ticket_data_voo_with_service_numbers
        service_number_site_map = {"1235": site_id, "4366": site_id}

        existing_tickets = [existing_ticket]
        inference_data = make_inference_data(
            predicted_class=predicted_class,
            filter_flags=filter_flags,
            potential_service_numbers=existing_ticket["service_numbers"],
        )

        expected_tickets_could_be_updated = [
            TicketOutput(
                site_id=site_id,
                service_numbers=existing_ticket["service_numbers"],
                ticket_id=existing_ticket["ticket_id"],
            )
        ]

        potential_tickets_output = repair_tickets_monitor._get_potential_tickets(
            inference_data, service_number_site_map, existing_tickets
        )

        assert potential_tickets_output.tickets_could_be_created == []
        assert potential_tickets_output.tickets_could_be_updated == expected_tickets_could_be_updated

    def _get_potential_tickets__could_be_created_tickets_test(
        self,
        repair_tickets_monitor,
        make_filter_flags,
        make_inference_data,
    ):
        predicted_class = "VOO"
        filter_flags = make_filter_flags(in_validation_set=True)
        site_id = "5678"
        service_numbers = ["1234", "2345"]
        service_number_site_map = {"1234": site_id, "2345": site_id}

        existing_tickets = []
        inference_data = make_inference_data(
            predicted_class=predicted_class,
            filter_flags=filter_flags,
            potential_service_numbers=service_numbers,
        )

        expected_tickets_could_be_created = [
            TicketOutput(
                site_id="5678",
                service_numbers=service_numbers,
            )
        ]

        potential_tickets_output = repair_tickets_monitor._get_potential_tickets(
            inference_data, service_number_site_map, existing_tickets
        )

        assert potential_tickets_output.tickets_could_be_created == expected_tickets_could_be_created
        assert potential_tickets_output.tickets_could_be_updated == []

    def _get_class_other_tickets_test(self, repair_tickets_monitor):
        service_number_site_map = {"1234": "4578"}

        expected_tickets = [TicketOutput(site_id="4578", service_numbers=["1234"], reason="predicted class is Other")]

        result_tickets = repair_tickets_monitor._get_class_other_tickets(service_number_site_map)

        assert expected_tickets == result_tickets

    @pytest.mark.parametrize(
        "ticket, site_ids, predicted_class,expected",
        [
            ({"site_id": "1234", "category": "Other"}, {"1234"}, "VAS", False),
            ({"site_id": "5890", "category": "VOO"}, {"1234"}, "VAS", False),
            ({"site_id": "1234", "category": "VAS"}, {"1234"}, "VAS", True),
            ({"site_id": "1234", "category": "VOO"}, {"1234"}, "VOO", True),
            ({"site_id": "1234", "category": "VAS"}, {"1234"}, "VOO", False),
            ({"site_id": "1234", "category": "VOO"}, {"1234"}, "VAS", True),
        ],
    )
    def _should_update_ticket_test(self, repair_tickets_monitor, ticket, site_ids, predicted_class, expected):
        result = repair_tickets_monitor._should_update_ticket(ticket, site_ids, predicted_class)
        assert result == expected

    @pytest.mark.parametrize(
        "predicted_class, filter_flags, expected",
        [
            (
                "Other",
                {
                    "is_filtered": False,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": False,
                },
                False,
            ),
            (
                "VOO",
                {
                    "is_filtered": True,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": False,
                },
                False,
            ),
            (
                "VOO",
                {
                    "is_filtered": False,
                    "in_validation_set": True,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": False,
                },
                False,
            ),
            (
                "VAS",
                {
                    "is_filtered": False,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": True,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": False,
                },
                False,
            ),
            (
                "VAS",
                {
                    "is_filtered": False,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": True,
                    "rta_model2_is_below_threshold": False,
                },
                False,
            ),
            # Model 2 is not checked now
            (
                "VOO",
                {
                    "is_filtered": False,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": True,
                },
                True,
            ),
            (
                "VAS",
                {
                    "is_filtered": False,
                    "in_validation_set": False,
                    "tagger_is_below_threshold": False,
                    "rta_model1_is_below_threshold": False,
                    "rta_model2_is_below_threshold": False,
                },
                True,
            ),
        ],
    )
    def _is_inference_actionable_test(
        self,
        repair_tickets_monitor,
        predicted_class,
        filter_flags,
        expected,
    ):
        inference_data = {
            "filter_flags": filter_flags,
            "predicted_class": predicted_class,
        }

        result = repair_tickets_monitor._is_inference_actionable(inference_data)
        assert result == expected

    def _compose_bec_note_text_update_test(self, repair_tickets_monitor):
        body = "<html><body>algo</body></html>"
        note_text = repair_tickets_monitor._compose_bec_note_text(
            email=AnyEmail(
                subject="Example subject",
                sender_address="from@address.com",
                body=body,
                date="2022-01-11 00:00:00",
            ),
            is_update_note=True,
        )

        expected_body = html2text.html2text(body)
        assert note_text == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "BEC AI RTA",
                "",
                "This note is new commentary from the client and posted via BEC AI engine.",
                "Please review the full narrative provided in the email attached:\n" "From: from@address.com",
                "Date Stamp: 2022-01-11 00:00:00",
                "Subject: Example subject",
                f"Body: \n {expected_body}",
            ]
        )

    def _compose_bec_note_to_ticket_update_test(self, repair_tickets_monitor):
        notes = repair_tickets_monitor._compose_bec_note_to_ticket(
            ticket_id="1234",
            service_numbers=["VC05200011984"],
            email=AnyEmail(),
            is_update_note=True,
        )

        assert all(
            "This note is new commentary from the client and posted via BEC AI engine." in note["text"]
            for note in notes
        )
        assert all(note["service_number"] == "VC05200011984" for note in notes)

    def _compose_bec_private_note_to_ticket_create_test(self, repair_tickets_monitor):
        # Given
        notes = repair_tickets_monitor._compose_bec_note_to_ticket(
            ticket_id="1234",
            service_numbers=["VC05200011984"],
            email=AnyEmail(),
            is_update_note=False,
        )

        assert all("This ticket was opened via MetTel Email Center AI Engine." in note["text"] for note in notes)
        assert all(note["service_number"] == "VC05200011984" for note in notes)

    @pytest.mark.asyncio
    async def _create_tickets_create_test(self, repair_tickets_monitor):
        # given
        site_id = "any_site_id"
        ticket_id = "any_ticket_id"
        upserted_ticket = UpsertedTicket(status=UpsertedStatus.created, ticket_id=ticket_id)
        repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(return_value=upserted_ticket)
        repair_tickets_monitor._subscribe_user_rpc = AsyncMock()

        # when
        response = await repair_tickets_monitor._create_tickets(AnyEmail(), {"1": site_id, "6": site_id})

        # then
        repair_tickets_monitor._subscribe_user_rpc.assert_awaited_once_with(ticket_id=ticket_id, user_email=ANY)
        assert response == CreateTicketsOutput(
            tickets_created=[TicketOutput(site_id=site_id, ticket_id=ticket_id, service_numbers=["1", "6"])],
        )

    @pytest.mark.asyncio
    async def _create_reply_tickets_is_properly_post_processed_test(self, repair_tickets_monitor):
        # given
        site_id = "any_site_id"
        ticket_id = "any_ticket_id"
        service_numbers = {"1": site_id, "6": site_id}
        parent_email = AnyEmail(id="any_parent_email")
        reply_email = AnyEmail(id="any_reply_email", parent=parent_email)

        upserted_ticket = UpsertedTicket(status=UpsertedStatus.created, ticket_id=ticket_id)
        repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(return_value=upserted_ticket)
        repair_tickets_monitor._subscribe_user_rpc = AsyncMock()

        bruin_repository = Mock(BruinRepository)
        bruin_repository.append_notes_to_ticket = AsyncMock()
        bruin_repository.link_email_to_ticket = AsyncMock()
        repair_tickets_monitor._bruin_repository = bruin_repository

        repair_tickets_monitor._compose_bec_note_to_ticket = case(
            given(
                ticket_id=ticket_id,
                service_numbers=["1", "6"],
                email=reply_email,
                is_update_note=False,
            ).returns("reply_note"),
            given(
                ticket_id=ticket_id,
                service_numbers=["1", "6"],
                email=parent_email,
                is_update_note=False,
            ).returns("parent_note"),
        )

        # when
        await repair_tickets_monitor._create_tickets(reply_email, service_numbers)

        # then
        append_notes_to_ticket_calls = [call(ticket_id, "reply_note"), call(ticket_id, "parent_note")]
        link_email_to_ticket_calls = [call(ticket_id, reply_email.id), call(ticket_id, parent_email.id)]

        assert bruin_repository.append_notes_to_ticket.call_count == 2
        assert bruin_repository.link_email_to_ticket.call_count == 2
        bruin_repository.append_notes_to_ticket.assert_has_awaits(append_notes_to_ticket_calls, any_order=True)
        bruin_repository.link_email_to_ticket.assert_has_awaits(link_email_to_ticket_calls, any_order=True)
        repair_tickets_monitor._subscribe_user_rpc.assert_awaited_once_with(
            ticket_id=ticket_id,
            user_email=reply_email.sender_address,
        )

    @pytest.mark.asyncio
    async def _create_parent_tickets_is_properly_post_processed_test(self, repair_tickets_monitor):
        # given
        site_id = "any_site_id"
        ticket_id = "any_ticket_id"
        service_numbers = {"1": site_id, "6": site_id}
        parent_email = AnyEmail(id="any_parent_email")

        upserted_ticket = UpsertedTicket(status=UpsertedStatus.created, ticket_id=ticket_id)
        repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(return_value=upserted_ticket)
        repair_tickets_monitor._subscribe_user_rpc = AsyncMock()

        bruin_repository = Mock(BruinRepository)
        bruin_repository.append_notes_to_ticket = AsyncMock()
        bruin_repository.link_email_to_ticket = AsyncMock()
        repair_tickets_monitor._bruin_repository = bruin_repository

        repair_tickets_monitor._compose_bec_note_to_ticket = given(
            ticket_id=ticket_id,
            service_numbers=["1", "6"],
            email=parent_email,
            is_update_note=False,
        ).returns("parent_note")

        # when
        await repair_tickets_monitor._create_tickets(parent_email, service_numbers)

        # then
        bruin_repository.append_notes_to_ticket.assert_awaited_once_with(ticket_id, "parent_note")
        bruin_repository.link_email_to_ticket.assert_awaited_once_with(ticket_id, parent_email.id)
        repair_tickets_monitor._subscribe_user_rpc.assert_awaited_once_with(
            ticket_id=ticket_id,
            user_email=parent_email.sender_address,
        )

    @pytest.mark.asyncio
    async def _create_tickets_update_test(self, repair_tickets_monitor):
        # given
        site_id = "any_site_id"
        ticket_id = "any_ticket_id"
        upserted_ticket = UpsertedTicket(status=UpsertedStatus.updated, ticket_id=ticket_id)
        repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(return_value=upserted_ticket)

        # when
        response = await repair_tickets_monitor._create_tickets(AnyEmail(), {"1": site_id, "6": site_id})

        # then
        repair_tickets_monitor._subscribe_user_rpc.assert_awaited_once_with(ticket_id=ticket_id, user_email=ANY)
        assert response == CreateTicketsOutput(
            tickets_updated=[
                TicketOutput(
                    site_id=site_id, ticket_id=ticket_id, service_numbers=["1", "6"], reason="update_with_asset_found"
                )
            ],
        )

    @pytest.mark.asyncio
    async def _create_tickets_error_test(self, repair_tickets_monitor):
        repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(side_effect=RpcError)

        response = await repair_tickets_monitor._create_tickets(AnyEmail(), {"1": "site_1", "6": "site_1"})

        repair_tickets_monitor._subscribe_user_rpc.assert_not_awaited()
        assert response == CreateTicketsOutput(
            tickets_cannot_be_created=[
                TicketOutput(site_id="site_1", service_numbers=["1", "6"], reason="Error while creating bruin ticket")
            ],
        )

    @pytest.mark.asyncio
    async def tickets_only_not_actionable_inferences_are_properly_handled_test(
        self,
        repair_tickets_monitor,
        make_filter_flags,
        make_inference_data,
    ):
        email_id = "1234"
        email = AnyEmail("1234")
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(
            potential_tickets_numbers=["1234"],
            filter_flags=filter_flags,
            predicted_class="Other",
        )
        repair_tickets_monitor._new_tagged_emails_repository = Mock()
        repair_tickets_monitor._save_output = AsyncMock()
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)
        repair_tickets_monitor._bruin_repository.get_single_ticket_basic_info = AsyncMock(
            return_value={
                "status": 200,
                "body": {"ticket_id": "1234", "ticket_status": "InProgress", "call_type": "REP", "category": "VOO"},
            }
        )

        await repair_tickets_monitor._process_repair_email(email)

        expected_output = RepairEmailOutput(
            email_id=email_id,
            tickets_could_be_updated=[TicketOutput(ticket_id="1234")],
            validated_tickets=[Ticket(id="1234", status=TicketStatus.IN_PROGRESS, call_type="REP", category="VOO")],
        )
        repair_tickets_monitor._save_output.assert_awaited_once_with(expected_output)

    @pytest.mark.asyncio
    async def no_validated_service_numbers_test(
        self,
        repair_tickets_monitor,
        make_filter_flags,
        make_inference_data,
    ):
        email_id = "1234"
        email = AnyEmail(id=email_id)
        filter_flags = make_filter_flags(
            tagger_is_below_threshold=True,
            rta_model1_is_below_threshold=True,
            rta_model2_is_below_threshold=True,
            is_filtered=True,
            in_validation_set=True,
        )
        inference_data = make_inference_data(
            potential_service_numbers=["1234"],
            filter_flags=filter_flags,
            predicted_class="Other",
        )
        repair_tickets_monitor._get_valid_service_numbers_site_map = AsyncMock(return_value={})
        repair_tickets_monitor._save_output = AsyncMock()
        repair_tickets_monitor._get_inference = AsyncMock(return_value=inference_data)

        await repair_tickets_monitor._process_repair_email(email)

        expected_output = RepairEmailOutput(
            email_id=email_id, tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")]
        )
        repair_tickets_monitor._save_output.assert_awaited_once_with(expected_output)

    @pytest.mark.asyncio
    async def get_tickets_test(self, repair_tickets_monitor):
        tickets_id = ["12345"]
        rpc_response_200 = {
            "status": 200,
            "body": {
                "ticketStatus": "New",
                "callType": "repair",
                "category": "VOO",
                "createDate": "2021-01-01",
            },
        }

        response = Mock()
        response.data = json.dumps(rpc_response_200).encode()
        repair_tickets_monitor._bruin_repository._event_bus.request = AsyncMock(return_value=response)
        tickets = await repair_tickets_monitor._get_tickets("1234", tickets_id)

        assert tickets == [Ticket(id="12345", status=TicketStatus.NEW, call_type="repair", category="VOO")]
