from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories import t7_repository as t7_repository_module
from application.repositories.t7_repository import T7Repository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(t7_repository_module, 'uuid', return_value=uuid_)


class TestT7Repository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        assert t7_repository._event_bus is event_bus
        assert t7_repository._logger is logger
        assert t7_repository._config is config
        assert t7_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_prediction_test(self):
        ticket_id = 12345

        ticket_rows = {
            "request_id": uuid_,
            "body": [
                {
                    "Asset": None,
                    "Ticket Status": "To do"
                },
                {
                    "Asset": "VC1234564",
                    "Ticket Status": "In Progress"
                },
                {
                    "Asset": "VC1234567",
                    "Ticket Status": "Done"
                }],
            'status': 200
        }

        assets_to_predict = ["VC1234564", "VC1234567"]

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows,
                'assets_to_predict': assets_to_predict,
            },
        }

        response = {
            'request_id': uuid_,
            'body': [
                {
                    'assetId': 'VC1234567',
                    'predictions': [
                        {
                            'name': 'Repair Completed',
                            'probability': 0.9484384655952454
                        },
                    ]
                }
            ],
            'status': 200
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, ticket_rows, assets_to_predict)

        event_bus.rpc_request.assert_awaited_once_with("t7.prediction.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_prediction_with_rpc_request_failing_test(self):
        ticket_id = 12345
        ticket_rows = []
        assets_to_predict = []

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows,
                'assets_to_predict': assets_to_predict
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, ticket_rows, assets_to_predict)

        event_bus.rpc_request.assert_awaited_once_with("t7.prediction.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        ticket_rows = []
        assets_to_predict = []
        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows,
                'assets_to_predict': assets_to_predict,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from T7',
            'status': 500
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id, ticket_rows, assets_to_predict)

        event_bus.rpc_request.assert_awaited_once_with("t7.prediction.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
