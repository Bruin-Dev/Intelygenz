from unittest.mock import patch

import asyncio
import pytest
from asynctest import CoroutineMock
from shortuuid import uuid

from application.domain.repair_email_output import RepairEmailOutput, TicketOutput
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from config import testconfig as config

uuid_ = uuid()
uuid_patch = patch("application.repositories.repair_ticket_kre_repository.uuid", return_value=uuid_)


class TestRepairTicketRepository:
    def instance_test(self, event_bus, logger, notifications_repository):
        repair_ticket_repository = RepairTicketKreRepository(event_bus, logger, config, notifications_repository)

        assert repair_ticket_repository._event_bus is event_bus
        assert repair_ticket_repository._logger is logger
        assert repair_ticket_repository._config is config
        assert repair_ticket_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_email_inference__ok_test(
        self,
        event_bus,
        repair_ticket_kre_repository,
        make_email,
        make_rpc_request,
        make_rpc_response,
        make_inference_data,
        make_inference_request_payload,
    ):
        email_id = "1234"
        client_id = "2145"
        tag_info = {"email_id": email_id, "type": "Repair", "tag_probability": 0.9}
        email_data = make_email(email_id=email_id, client_id=client_id, body="Test", from_address="test@test.com")
        inference_data = make_inference_data()
        payload = make_inference_request_payload(email_data=email_data, tag_info=tag_info)
        expected_request = make_rpc_request(request_id=uuid_, **payload)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=inference_data)
        event_bus.rpc_request.return_value = expected_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.get_email_inference(email_data["email"], tag_info)

        event_bus.rpc_request.assert_awaited_once(
            "rta.prediction.request", expected_request, config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"]
        )

        assert response["status"] == 200
        assert response["body"] == inference_data

    @pytest.mark.asyncio
    async def get_email_inference__not_2XX_test(
        self,
        event_bus,
        repair_ticket_kre_repository,
        make_email,
        make_rpc_request,
        make_rpc_response,
        make_inference_request_payload,
    ):
        email_id = "1234"
        client_id = "2145"
        tag_info = {"email_id": email_id, "type": "Repair", "tag_probability": 0.9}
        email_data = make_email(email_id=email_id, client_id=client_id, body="Test", from_address="test@test.com")
        error_response_body = "Error"
        payload = make_inference_request_payload(email_data=email_data, tag_info=tag_info)

        expected_request = make_rpc_request(request_id=uuid_, **payload)
        expected_response = make_rpc_response(request_id=uuid_, status=400, body=error_response_body)
        event_bus.rpc_request.return_value = expected_response

        repair_ticket_kre_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_patch:
            response = await repair_ticket_kre_repository.get_email_inference(email_data["email"], tag_info)

        repair_ticket_kre_repository._notifications_repository.send_slack_message.assert_awaited_once()
        event_bus.rpc_request.assert_awaited_once(
            "rta.prediction.request", expected_request, config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"]
        )

        assert response["status"] == 400
        assert response["body"] == "Error"

    @pytest.mark.asyncio
    async def save_created_ticket_feedback__ok_test(
        self, event_bus, repair_ticket_kre_repository, make_email, make_rpc_request, make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        client_id = 8935
        ticket_data = {"ticket_id": ticket_id, "service_numbers": ["1234", "1235"], "category": "VOO"}
        email_data = make_email(email_id=email_id, parent_id=email_id, client_id=client_id)["email"]
        site_map = {"1234": "site1", "5678": "site2"}

        rpc_request = make_rpc_request(original_email=email_data, ticket=ticket_data)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body="ok")

        event_bus.rpc_request.return_value = expected_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_created_ticket_feedback(
                email_data, ticket_data, site_map
            )

        event_bus.rpc_request.assert_awaited_once(
            "repair_ticket_automation.save_created_tickets.request",
            rpc_request,
            config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"],
        )

        assert response == expected_response

    @pytest.mark.asyncio
    async def save_created_ticket_feedback__not_2XX_test(
        self, event_bus, repair_ticket_kre_repository, notifications_repository, make_email, make_rpc_response
    ):
        ticket_id = 1234
        email_id = 5678
        client_id = 8935
        ticket_data = {"ticket_id": ticket_id, "service_numbers": ["1234", "1235"], "category": "VOO"}
        email_data = make_email(email_id=email_id, parent_id=email_id, client_id=client_id)["email"]
        site_map = {"1234": "site1", "5678": "site2"}

        error_response = make_rpc_response(request_id=uuid_, status=400, body="Failed")
        event_bus.rpc_request.return_value = error_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_created_ticket_feedback(
                email_data, ticket_data, site_map
            )

        event_bus.rpc_request.assert_awaited()
        assert event_bus.rpc_request.await_count == 2
        notifications_repository.send_slack_message.assert_awaited_once()

        assert response == error_response

    @pytest.mark.asyncio
    async def save_outputs__ok_test(self, repair_ticket_kre_repository, make_rta_ticket_payload, make_rpc_response):
        email_id = "1234"
        validated_service_numbers = ["1234", "4567"]
        service_numbers_sites_map = {"1234": "site_1", "5678": "site_1"}
        tickets_created = [TicketOutput(site_id="site_1", service_numbers=validated_service_numbers)]

        rpc_response = make_rpc_response(request_id=uuid_, status=200, body={"success": True})

        with patch.object(
            repair_ticket_kre_repository._event_bus, "rpc_request", return_value=asyncio.Future()
        ) as rpc_request_mock:
            rpc_request_mock.return_value.set_result(rpc_response)
            save_output_response = await repair_ticket_kre_repository.save_outputs(
                RepairEmailOutput(
                    email_id=email_id,
                    service_numbers_sites_map=service_numbers_sites_map,
                    tickets_created=tickets_created,
                )
            )

        assert save_output_response["status"] == 200

    @pytest.mark.asyncio
    async def save_outputs__not_200_test(
        self, repair_ticket_kre_repository, make_rta_ticket_payload, make_rpc_response
    ):
        email_id = "1234"

        validated_service_numbers = ["1234", "4567"]
        service_numbers_sites_map = {"1234": "site_1", "5678": "site_1"}
        tickets_created = [TicketOutput(site_id="site_1", service_numbers=validated_service_numbers)]
        rpc_response = make_rpc_response(request_id=uuid_, status=400, body="Error")

        with patch.object(
            repair_ticket_kre_repository._event_bus, "rpc_request", return_value=asyncio.Future()
        ) as rpc_request_mock:
            rpc_request_mock.return_value.set_result(rpc_response)
            save_output_response = await repair_ticket_kre_repository.save_outputs(
                RepairEmailOutput(
                    email_id=email_id,
                    service_numbers_sites_map=service_numbers_sites_map,
                    tickets_created=tickets_created,
                )
            )

        assert save_output_response["status"] == 400
        assert save_output_response["body"] == "Error"

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback__ok_test(self, event_bus, repair_ticket_kre_repository, make_rpc_response):
        ticket_id = 1235
        client_id = 5679
        ticket_status = "cancelled"
        cancellation_reasons = ["reason 1"]

        response = make_rpc_response(status=200, body={"success": True})

        event_bus.rpc_request.return_value = response

        result = await repair_ticket_kre_repository.save_closed_ticket_feedback(
            ticket_id, client_id, ticket_status, cancellation_reasons
        )

        assert result["status"] == 200
        assert result["body"] == {"success": True}

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback__not_2xx_test(
        self,
        event_bus,
        repair_ticket_kre_repository,
        notifications_repository,
        make_rpc_response,
    ):
        ticket_id = 1235
        client_id = 5679
        ticket_status = "resolved"
        cancellation_reasons = []

        response = make_rpc_response(status=500, body="Error")

        event_bus.rpc_request.return_value = response
        notifications_repository.send_slack_message = CoroutineMock()

        result = await repair_ticket_kre_repository.save_closed_ticket_feedback(
            ticket_id, client_id, ticket_status, cancellation_reasons
        )

        notifications_repository.send_slack_message.assert_awaited_once()

        assert result["status"] == 500
        assert result["body"] == "Error"
