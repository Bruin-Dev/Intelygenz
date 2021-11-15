from unittest.mock import patch

from asynctest import CoroutineMock
import pytest
from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from config import testconfig as config


uuid_ = uuid()
uuid_patch = patch('application.repositories.repair_ticket_kre_repository.uuid', return_value=uuid_)


class TestRepairTicketRepository:

    def instance_test(self, event_bus, logger, notifications_repository):
        repair_ticket_repository = RepairTicketKreRepository(event_bus, logger, config, notifications_repository)

        assert repair_ticket_repository._event_bus is event_bus
        assert repair_ticket_repository._logger is logger
        assert repair_ticket_repository._config is config
        assert repair_ticket_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def save_created_ticket_feedback__ok_test(
            self,
            event_bus,
            repair_ticket_kre_repository,
            make_email,
            make_rpc_request,
            make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        ticket_data = {"ticket_id": ticket_id}
        email_data = make_email(email_id=email_id)

        rpc_request = make_rpc_request(original_email=email_data, ticket=ticket_data)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body="ok")

        event_bus.rpc_request.return_value = expected_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_created_ticket_feedback(email_data, ticket_data)

        event_bus.rpc_request.assert_awaited_once(
            "repair_ticket_automation.save_created_tickets.request",
            rpc_request,
            config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']
        )

        assert response == expected_response

    @pytest.mark.asyncio
    async def save_created_ticket_feedback__not_2XX_test(
            self,
            event_bus,
            repair_ticket_kre_repository,
            notifications_repository,
            make_email,
            make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        ticket_data = {"ticket_id": ticket_id}
        email_data = make_email(email_id=email_id)

        error_response = make_rpc_response(request_id=uuid_, status=400, body="Failed")
        event_bus.rpc_request.return_value = error_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_created_ticket_feedback(email_data, ticket_data)

        event_bus.rpc_request.assert_awaited()
        assert event_bus.rpc_request.await_count == 2
        notifications_repository.send_slack_message.assert_awaited_once()

        assert response == error_response
