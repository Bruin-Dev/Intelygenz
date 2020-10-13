from unittest.mock import Mock, call
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

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }
        bruin_tickets_get_response = {
            "request_id": uuid_,
            "body": [
                {
                    "Asset": None,
                    "Ticket Status": "To do"
                },
                {
                    "Asset": "asset4",
                    "Ticket Status": "In Progress"
                },
                {
                    "Asset": "asset7",
                    "Ticket Status": "Done"
                }],
            'status': 200
        }

        t7_prediction_response = {
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
        event_bus.rpc_request = CoroutineMock(side_effect=[
            bruin_tickets_get_response,
            t7_prediction_response
        ])

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id)

        assert event_bus.rpc_request.await_count == 2
        assert event_bus.rpc_request.call_count == 2
        assert event_bus.rpc_request.call_args_list[0] == call(
            "bruin.ticket.get.task.history",
            request,
            timeout=60
        )

        request["body"]["ticket_rows"] = bruin_tickets_get_response["body"]
        assert event_bus.rpc_request.call_args_list[1] == call(
            "t7.prediction.request",
            request,
            timeout=60
        )

        assert result == t7_prediction_response

    @pytest.mark.asyncio
    async def get_prediction_with_rpc_request_failing_test(self):
        ticket_id = 12345

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }

        bruin_tickets_get_response = {
            "request_id": uuid_,
            "body": [],
            'status': 200
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            bruin_tickets_get_response,
            Exception
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id)

        assert event_bus.rpc_request.await_count == 2
        assert event_bus.rpc_request.call_count == 2
        assert event_bus.rpc_request.call_args_list[0] == call(
            "bruin.ticket.get.task.history",
            request,
            timeout=60
        )

        request["body"]["ticket_rows"] = bruin_tickets_get_response["body"]

        assert event_bus.rpc_request.call_args_list[1] == call(
            "t7.prediction.request",
            request,
            timeout=60
        )

        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response


    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }

        bruin_tickets_get_response = {
            "request_id": uuid_,
            "body": [],
            'status': 200
        }

        response = {
            'request_id': uuid_,
            'body': 'Got internal error from T7',
            'status': 500
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            bruin_tickets_get_response,
            response
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.get_prediction(ticket_id)

        assert event_bus.rpc_request.await_count == 2
        assert event_bus.rpc_request.call_count == 2
        assert event_bus.rpc_request.call_args_list[0] == call(
            "bruin.ticket.get.task.history",
            request,
            timeout=60
        )

        request["body"]["ticket_rows"] = bruin_tickets_get_response["body"]

        assert event_bus.rpc_request.call_args_list[1] == call(
            "t7.prediction.request",
            request,
            timeout=60
        )

        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
