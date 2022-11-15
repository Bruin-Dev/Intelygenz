from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import nats_error_response
from application.repositories import t7_repository as t7_repository_module
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(t7_repository_module, "uuid", return_value=uuid_)


class TestT7Repository:
    def instance_test(self, t7_repository, nats_client, notifications_repository):
        assert t7_repository._nats_client is nats_client
        assert t7_repository._config is testconfig
        assert t7_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_prediction_test(
        self,
        t7_repository,
        make_task_history_item,
        make_task_history,
        make_rpc_request,
        make_rpc_response,
        make_prediction_object,
        serial_number_1,
        serial_number_2,
        holmdel_noc_prediction,
    ):
        ticket_id = 12345

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history_item_2 = make_task_history_item(serial_number=serial_number_2)
        task_history = make_task_history(task_history_item_1, task_history_item_2)

        assets_to_predict = [serial_number_1, serial_number_2]

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            ticket_rows=task_history,
            assets_to_predict=assets_to_predict,
        )

        prediction_1 = make_prediction_object(serial_number=serial_number_1, predictions=[holmdel_noc_prediction])
        prediction_2 = make_prediction_object(serial_number=serial_number_2, predictions=[holmdel_noc_prediction])
        response = make_rpc_response(
            request_id=uuid_,
            body=[
                prediction_1,
                prediction_2,
            ],
            status=200,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        t7_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, task_history, assets_to_predict)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.prediction.request", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_prediction_with_rpc_request_failing_test(
        self,
        t7_repository,
        make_task_history_item,
        make_task_history,
        make_rpc_request,
        serial_number_1,
        serial_number_2,
    ):
        ticket_id = 12345

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history_item_2 = make_task_history_item(serial_number=serial_number_2)
        task_history = make_task_history(task_history_item_1, task_history_item_2)

        assets_to_predict = [serial_number_1, serial_number_2]

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            ticket_rows=task_history,
            assets_to_predict=assets_to_predict,
        )

        t7_repository._nats_client.request.side_effect = Exception
        t7_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, task_history, assets_to_predict)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.prediction.request", to_json_bytes(request), timeout=120
        )
        t7_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_prediction_with_rpc_request_returning_non_2xx_status_test(
        self,
        t7_repository,
        make_task_history_item,
        make_task_history,
        make_rpc_request,
        make_rpc_response,
        serial_number_1,
        serial_number_2,
    ):
        ticket_id = 12345

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history_item_2 = make_task_history_item(serial_number=serial_number_2)
        task_history = make_task_history(task_history_item_1, task_history_item_2)

        assets_to_predict = [serial_number_1, serial_number_2]

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            ticket_rows=task_history,
            assets_to_predict=assets_to_predict,
        )

        response = make_rpc_response(
            request_id=uuid_,
            body="Got internal error from T7",
            status=500,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        t7_repository._nats_client.request = AsyncMock(return_value=response_msg)

        t7_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, task_history, assets_to_predict)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.prediction.request", to_json_bytes(request), timeout=120
        )
        t7_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def post_live_automation_metrics_test(self, t7_repository, make_rpc_request, make_rpc_response):
        ticket_id = 12345
        asset_id = "VC000TEST"
        automated_successfully = False

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            asset_id=asset_id,
            automated_successfully=automated_successfully,
        )

        response = make_rpc_response(
            request_id=uuid_,
            body="Metric saved successfully",
            status=200,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        t7_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await t7_repository.post_live_automation_metrics(ticket_id, asset_id, automated_successfully)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.live.automation.metrics", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def post_live_automation_metrics_with_rpc_request_failing_test(self, t7_repository, make_rpc_request):
        ticket_id = 12345
        asset_id = "VC000TEST"
        automated_successfully = False

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            asset_id=asset_id,
            automated_successfully=automated_successfully,
        )

        t7_repository._nats_client.request.side_effect = Exception
        t7_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await t7_repository.post_live_automation_metrics(ticket_id, asset_id, automated_successfully)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.live.automation.metrics", to_json_bytes(request), timeout=120
        )
        t7_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def post_live_automation_metrics_with_rpc_request_returning_non_2xx_status_test(
        self, t7_repository, make_rpc_request, make_rpc_response
    ):
        ticket_id = 12345
        asset_id = "VC000TEST"
        automated_successfully = False

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            asset_id=asset_id,
            automated_successfully=automated_successfully,
        )

        response = make_rpc_response(
            request_id=uuid_,
            body="Got internal error from T7",
            status=500,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        t7_repository._nats_client.request = AsyncMock(return_value=response_msg)

        t7_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await t7_repository.post_live_automation_metrics(ticket_id, asset_id, automated_successfully)

        t7_repository._nats_client.request.assert_awaited_once_with(
            "t7.live.automation.metrics", to_json_bytes(request), timeout=120
        )
        t7_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
