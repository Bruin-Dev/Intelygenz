from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application.actions.new_closed_tickets_feedback import NewClosedTicketsFeedback
from asynctest import CoroutineMock
from config import testconfig as config
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch("application.actions.new_closed_tickets_feedback.uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def ticket_created_ai(make_ticket_decamelized):
    return make_ticket_decamelized(
        ticket_id=1234,
        ticket_status="Closed",
        client_id="5678",
        created_by="Intelygenz Ai",
        call_type="REP",
        category="VOO",
        severity=2,
    )


@pytest.fixture(scope="function")
def ticket_created_human(make_ticket_decamelized):
    return make_ticket_decamelized(
        ticket_id=1234,
        ticket_status="Closed",
        client_id="5678",
        created_by="Rando Guy",
        call_type="REP",
        category="VOO",
        severity=2,
    )


class TestNewClosedTicketsFeedback:
    def instance_test(self, event_bus, logger, scheduler, repair_ticket_kre_repository, bruin_repository):
        new_closed_tickets_feedback_instance = NewClosedTicketsFeedback(
            event_bus, logger, scheduler, config, repair_ticket_kre_repository, bruin_repository
        )

        assert new_closed_tickets_feedback_instance._event_bus is event_bus
        assert new_closed_tickets_feedback_instance._logger is logger
        assert new_closed_tickets_feedback_instance._scheduler is scheduler
        assert new_closed_tickets_feedback_instance._config is config
        assert new_closed_tickets_feedback_instance._rta_repository is repair_ticket_kre_repository
        assert new_closed_tickets_feedback_instance._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def start_closed_new_tickets_feedback_job_with_exec_on_start_test(
        self, new_closed_tickets_feedback, scheduler
    ):
        next_run_time = datetime.now()
        added_seconds = timedelta(0, 5)

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch("application.actions.new_closed_tickets_feedback.datetime", datetime_mock):
            await new_closed_tickets_feedback.start_closed_ticket_feedback(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            new_closed_tickets_feedback._run_closed_tickets_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["new_closed_tickets_feedback"],
            next_run_time=next_run_time + added_seconds,
            replace_existing=False,
            id="_run_closed_tickets_polling",
        )

    def get_igz_created_tickets__test(self, new_closed_tickets_feedback, ticket_created_ai, ticket_created_human):
        tickets = [ticket_created_human, ticket_created_ai]

        result = new_closed_tickets_feedback._get_igz_created_tickets(tickets)

        assert result == [ticket_created_ai]

    def get_igz_created_tickets__no_tickets_test(self, new_closed_tickets_feedback):
        tickets = []

        result = new_closed_tickets_feedback._get_igz_created_tickets(tickets)

        assert result == []

    @pytest.mark.asyncio
    async def get_closed_tickets_created_during_last_3_days__ok__test(
        self, new_closed_tickets_feedback, ticket_created_ai
    ):
        bruin_response = {"status": 200, "body": [ticket_created_ai]}

        bruin_repository = Mock()
        bruin_repository.get_closed_tickets_with_creation_date_limit = CoroutineMock(return_value=bruin_response)
        new_closed_tickets_feedback._bruin_repository = bruin_repository

        tickets = await new_closed_tickets_feedback.get_closed_tickets_created_during_last_3_days()

        assert tickets == [ticket_created_ai]

    @pytest.mark.asyncio
    async def get_closed_tickets_created_during_last_week__error_in_bruin_test(self, new_closed_tickets_feedback):
        bruin_response = {"status": 500, "body": "Error"}

        bruin_repository = Mock()
        bruin_repository.get_closed_tickets_with_creation_date_limit = CoroutineMock(return_value=bruin_response)
        new_closed_tickets_feedback._bruin_repository = bruin_repository

        tickets = await new_closed_tickets_feedback.get_closed_tickets_created_during_last_3_days()

        assert tickets == []

    @pytest.mark.asyncio
    async def run_closed_tickets_polling__ok_test(self, new_closed_tickets_feedback, ticket_created_ai):
        tickets = [ticket_created_ai]

        get_tickets_mock = CoroutineMock(return_value=tickets)
        save_tickets_mock = CoroutineMock(return_value=None)
        new_closed_tickets_feedback.get_closed_tickets_created_during_last_3_days = get_tickets_mock
        new_closed_tickets_feedback._save_closed_ticket_feedback = save_tickets_mock

        await new_closed_tickets_feedback._run_closed_tickets_polling()

        get_tickets_mock.assert_awaited_once()
        save_tickets_mock.assert_awaited_once_with(ticket_created_ai)

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback__ok_test(self, new_closed_tickets_feedback, ticket_created_ai):
        bruin_response_body = {"ticket_status": "resolved", "cancellation_reasons": []}
        bruin_response = {"status": 200, "body": bruin_response_body}

        kre_response = {"status": 200, "body": {"success": True}}

        bruin_repository = Mock()
        bruin_repository.get_status_and_cancellation_reasons = CoroutineMock(return_value=bruin_response)
        new_closed_tickets_feedback._bruin_repository = bruin_repository

        repair_ticket_kre_repository = Mock()
        repair_ticket_kre_repository.save_closed_ticket_feedback = CoroutineMock(return_value=kre_response)
        new_closed_tickets_feedback._rta_repository = repair_ticket_kre_repository

        await new_closed_tickets_feedback._save_closed_ticket_feedback(ticket_created_ai)

        bruin_repository.get_status_and_cancellation_reasons.assert_awaited_once_with(ticket_created_ai["ticket_id"])
        repair_ticket_kre_repository.save_closed_ticket_feedback.assert_awaited_once_with(
            ticket_created_ai["ticket_id"],
            ticket_created_ai["client_id"],
            bruin_response_body["ticket_status"],
            bruin_response_body["cancellation_reasons"],
        )

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback__bruin_status_and_reasons_error_test(
        self, new_closed_tickets_feedback, ticket_created_ai
    ):
        bruin_response = {"status": 500, "body": "Error"}

        bruin_repository = Mock()
        bruin_repository.get_status_and_cancellation_reasons = CoroutineMock(return_value=bruin_response)
        new_closed_tickets_feedback._bruin_repository = bruin_repository

        logger = Mock()
        new_closed_tickets_feedback._logger = logger

        repair_ticket_kre_repository = Mock()
        repair_ticket_kre_repository.save_closed_ticket_feedback = CoroutineMock()
        new_closed_tickets_feedback._rta_repository = repair_ticket_kre_repository

        await new_closed_tickets_feedback._save_closed_ticket_feedback(ticket_created_ai)

        bruin_repository.get_status_and_cancellation_reasons.assert_awaited_once_with(ticket_created_ai["ticket_id"])
        repair_ticket_kre_repository.save_closed_ticket_feedback.assert_not_awaited()
        logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback__rta_saving_error_test(self, new_closed_tickets_feedback, ticket_created_ai):
        bruin_response_body = {"ticket_status": "resolved", "cancellation_reasons": []}
        bruin_response = {"status": 200, "body": bruin_response_body}

        kre_response = {"status": 500, "body": "Error"}

        bruin_repository = Mock()
        bruin_repository.get_status_and_cancellation_reasons = CoroutineMock(return_value=bruin_response)
        new_closed_tickets_feedback._bruin_repository = bruin_repository

        logger = Mock()
        new_closed_tickets_feedback._logger = logger

        repair_ticket_kre_repository = Mock()
        repair_ticket_kre_repository.save_closed_ticket_feedback = CoroutineMock(return_value=kre_response)
        new_closed_tickets_feedback._rta_repository = repair_ticket_kre_repository

        await new_closed_tickets_feedback._save_closed_ticket_feedback(ticket_created_ai)

        bruin_repository.get_status_and_cancellation_reasons.assert_awaited_once_with(ticket_created_ai["ticket_id"])
        repair_ticket_kre_repository.save_closed_ticket_feedback.assert_awaited_once_with(
            ticket_created_ai["ticket_id"],
            ticket_created_ai["client_id"],
            bruin_response_body["ticket_status"],
            bruin_response_body["cancellation_reasons"],
        )
        logger.error.assert_called_once()
