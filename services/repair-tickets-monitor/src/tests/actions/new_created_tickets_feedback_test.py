from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.actions.new_created_tickets_feedback import NewCreatedTicketsFeedback
from config import testconfig as config
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch("application.actions.new_created_tickets_feedback.uuid", return_value=uuid_)


class TestNewCreatedTicketsFeedback:
    def instance_test(
        self,
        event_bus,
        scheduler,
        new_created_tickets_repository,
        repair_ticket_kre_repository,
        bruin_repository,
    ):
        new_created_tickets_feedback = NewCreatedTicketsFeedback(
            event_bus,
            scheduler,
            config,
            new_created_tickets_repository,
            repair_ticket_kre_repository,
            bruin_repository,
        )

        assert new_created_tickets_feedback._event_bus is event_bus
        assert new_created_tickets_feedback._scheduler is scheduler
        assert new_created_tickets_feedback._config is config
        assert new_created_tickets_feedback._new_created_tickets_repository is new_created_tickets_repository
        assert new_created_tickets_feedback._rta_repository is repair_ticket_kre_repository
        assert new_created_tickets_feedback._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def start_created_new_tickets_feedback_job_with_exec_on_start_test(
        self, new_created_tickets_feedback, scheduler
    ):
        next_run_time = datetime.now()
        added_seconds = timedelta(0, 5)

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch("application.actions.new_created_tickets_feedback.datetime", datetime_mock):
            await new_created_tickets_feedback.start_created_ticket_feedback(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            new_created_tickets_feedback._run_created_tickets_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["new_created_tickets_feedback"],
            next_run_time=next_run_time + added_seconds,
            replace_existing=False,
            id="_run_created_tickets_polling",
        )

    def _check_error_test(self, new_created_tickets_feedback):
        error_code = 404
        ticket_id = 1234
        email_id = 4567

        new_created_tickets_feedback._new_created_tickets_repository = Mock()
        new_created_tickets_repository = new_created_tickets_feedback._new_created_tickets_repository
        new_created_tickets_repository.increase_ticket_error_counter.return_value = 1000

        new_created_tickets_feedback._check_error(error_code, ticket_id, email_id)

        new_created_tickets_repository.delete_ticket_error_counter.assert_called_once_with(ticket_id, error_code)

    @pytest.mark.asyncio
    async def _save_created_ticket_feedback__ok_test(
        self, new_created_tickets_feedback, make_email, make_ticket_decamelized, make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        client_id = 4689
        email_data = make_email(email_id=email_id, client_id=client_id)["email"]
        ticket_input = {"ticket_id": ticket_id}

        # create ticket data
        ticket_data = make_ticket_decamelized(ticket_id=ticket_id)
        ticket_data["service_numbers"] = ["1234"]
        ticket_response = make_rpc_response(status=200, body=ticket_data)

        # site map response
        site_map = {"1234": "site_id"}

        rta_response = make_rpc_response(status=200, body={"success": True})
        get_site_map_mock = AsyncMock(return_value=site_map)

        new_created_tickets_feedback._bruin_repository = Mock()
        new_created_tickets_feedback._new_created_tickets_repository = Mock()
        new_created_tickets_feedback._rta_repository = Mock()
        new_created_tickets_feedback._get_site_map_for_ticket = get_site_map_mock

        rta_repository = new_created_tickets_feedback._rta_repository
        rta_repository.save_created_ticket_feedback = AsyncMock(return_value=rta_response)

        new_created_tickets_repository = new_created_tickets_feedback._new_created_tickets_repository

        bruin_repository = new_created_tickets_feedback._bruin_repository
        bruin_repository.get_single_ticket_info_with_service_numbers = AsyncMock(return_value=ticket_response)

        await new_created_tickets_feedback._save_created_ticket_feedback(email_data, ticket_input)

        get_site_map_mock.assert_awaited_once_with(client_id, ticket_data["service_numbers"])
        new_created_tickets_repository.mark_complete.assert_called_once_with(email_id, ticket_id)

    @pytest.mark.asyncio
    async def _save_created_ticket_feedback__404_ticket_body_test(
        self, new_created_tickets_feedback, make_email, make_ticket_decamelized, make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        email_data = make_email(email_id=email_id)["email"]
        ticket_data = make_ticket_decamelized(ticket_id=ticket_id)
        response = make_rpc_response(status=404, body="Not found")

        new_created_tickets_feedback._bruin_repository = Mock()
        new_created_tickets_feedback._new_created_tickets_repository = Mock()
        bruin_repository = new_created_tickets_feedback._bruin_repository
        bruin_repository.get_single_ticket_info_with_service_numbers = AsyncMock(return_value=response)
        new_created_tickets_feedback._new_created_tickets_repository.increase_ticket_error_counter.return_value = 1000

        await new_created_tickets_feedback._save_created_ticket_feedback(email_data, ticket_data)

        new_created_tickets_feedback._new_created_tickets_repository.mark_complete.assert_not_called()
        bruin_repository.get_single_ticket_info_with_service_numbers.assert_called_once()

    @pytest.mark.asyncio
    async def _get_site_map_for_ticket__ok_test(self, new_created_tickets_feedback, make_rpc_response):
        client_id = 1234
        service_numbers = ["5679"]
        expected_result = {"5679": "1234"}

        bruin_response = make_rpc_response(status=200, body={"site_id": 1234})

        bruin_repository_mock = Mock()
        bruin_repository_mock.verify_service_number_information = AsyncMock(return_value=bruin_response)
        new_created_tickets_feedback._bruin_repository = bruin_repository_mock

        results = await new_created_tickets_feedback._get_site_map_for_ticket(client_id, service_numbers)

        assert results == expected_result

    @pytest.mark.asyncio
    async def _get_site_map_for_ticket__all_errors_test(self, new_created_tickets_feedback, make_rpc_response):
        client_id = 1234
        service_numbers = ["5679"]

        bruin_response = make_rpc_response(status=400, body="Error")

        bruin_repository_mock = Mock()
        bruin_repository_mock.verify_service_number_information = AsyncMock(return_value=bruin_response)

        results = await new_created_tickets_feedback._get_site_map_for_ticket(client_id, service_numbers)

        assert results == {}
