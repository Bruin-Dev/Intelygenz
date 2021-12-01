from unittest.mock import patch

import pytest
from shortuuid import uuid
from asynctest import CoroutineMock

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
        tag_info = {"email_id": email_id, "tag_id": "1", "probability": 0.9}
        email_data = make_email(email_id=email_id)
        inference_data = make_inference_data()
        payload = make_inference_request_payload(email_data=email_data, tag_info=tag_info)
        expected_request = make_rpc_request(request_id=uuid_, **payload)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=inference_data)
        event_bus.rpc_request.return_value = expected_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.get_email_inference(email_data, tag_info)

        event_bus.rpc_request.assert_awaited_once(
            "rta.prediction.request",
            expected_request,
            config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']
        )

        assert response

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
        tag_info = {"email_id": email_id, "tag_id": "1", "probability": 0.9}
        email_data = make_email(email_id=email_id)
        error_response_body = {"Error": "Error"}
        payload = make_inference_request_payload(email_data=email_data, tag_info=tag_info)

        expected_request = make_rpc_request(request_id=uuid_, **payload)
        expected_response = make_rpc_response(request_id=uuid_, status=400, body=error_response_body)
        event_bus.rpc_request.return_value = expected_response

        repair_ticket_kre_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_patch:
            response = await repair_ticket_kre_repository.get_email_inference(email_data, tag_info)

        repair_ticket_kre_repository._notifications_repository.send_slack_message.assert_awaited_once()
        event_bus.rpc_request.assert_awaited_once(
            "rta.prediction.request",
            expected_request,
            config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']
        )

        assert response

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

    @pytest.mark.asyncio
    async def save_outputs__ok_test(
            self,
            event_bus,
            repair_ticket_kre_repository,
            make_save_outputs_request_payload,
            make_rta_kre_ticket_payload,
            make_rpc_request,
            make_rpc_response
    ):
        email_id = "1234"

        validated_service_numbers = ["1234", "4567"]
        service_numbers_sites_map = {"1234": "site_1", "5678": "site_1"}
        tickets_created = make_rta_kre_ticket_payload(
            site_id="site_1",
            service_numbers=validated_service_numbers
        )
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []

        expected_payload = make_save_outputs_request_payload(
            email_id=email_id,
            service_numbers=validated_service_numbers,
            service_numbers_sites_map=service_numbers_sites_map,
            tickets_created=tickets_created,
            tickets_updated=tickets_updated,
            tickets_could_be_created=tickets_could_be_created,
            tickets_could_be_updated=tickets_could_be_updated,
            tickets_cannot_be_created=tickets_cannot_be_created,
        )
        rpc_request = make_rpc_request(request_id=uuid_, **expected_payload)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body={"success": True})

        event_bus.rpc_request.return_value = expected_response

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_outputs(
                email_id,
                service_numbers_sites_map,
                tickets_created,
                tickets_updated,
                tickets_could_be_created,
                tickets_could_be_updated,
                tickets_cannot_be_created,
            )

        event_bus.rpc_request.assert_awaited_once(
            "repair_ticket_automation.save_created_tickets.request",
            rpc_request,
            config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']
        )

        assert response == expected_response

    @pytest.mark.asyncio
    async def save_outputs__not_2XX_test(
            self,
            event_bus,
            repair_ticket_kre_repository,
            make_rta_kre_ticket_payload,
            make_rpc_response
    ):
        email_id = "1234"

        validated_service_numbers = ["1234", "4567"]
        service_numbers_sites_map = {"1234": "site_1", "5678": "site_1"}
        tickets_created = make_rta_kre_ticket_payload(
            site_id="site_1",
            service_numbers=validated_service_numbers
        )
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []

        expected_response = make_rpc_response(request_id=uuid_, status=400, body="Error")
        event_bus.rpc_request.return_value = expected_response
        repair_ticket_kre_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_patch:
            response = await repair_ticket_kre_repository.save_outputs(
                email_id,
                service_numbers_sites_map,
                tickets_created,
                tickets_updated,
                tickets_could_be_created,
                tickets_could_be_updated,
                tickets_cannot_be_created,
            )

        repair_ticket_kre_repository._notifications_repository.send_slack_message.assert_awaited_once()

        assert response['status'] == 400
        assert response['body'] == 'Error'
