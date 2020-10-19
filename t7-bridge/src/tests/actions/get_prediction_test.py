from unittest.mock import Mock

import pytest
from application.actions.get_prediction import GetPrediction
from asynctest import CoroutineMock


class TestGetPrediction:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        t7_repository = Mock()
        t7_kre_repository = Mock()

        prediction = GetPrediction(logger, config, event_bus, t7_repository, t7_kre_repository)

        assert prediction._config == config
        assert prediction._logger == logger
        assert prediction._event_bus == event_bus
        assert prediction._t7_repository == t7_repository
        assert prediction._t7_kre_repository == t7_kre_repository

    @pytest.mark.asyncio
    async def get_prediction_with_no_body_in_request_message_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock()

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository, t7_kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        prediction_action._t7_repository.get_prediction.assert_not_called()
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": {"ticket_id"}..} in the request',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def get_prediction_with_no_ticket_id_in_body_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': {
                'some-key': 'some-data',
            },
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()
        logger.info = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock()

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository, t7_kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        prediction_action._t7_repository.get_prediction.assert_not_called()
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": {"ticket_id"}..} in the request',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def get_prediction_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()

        request_id = 123
        ticket_id = 321
        ticket_rows = [
            {
                "Asset": "asset1",
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 1",
                "Task Result": None,
                "Ticket Status": "Closed",
            },
            {
                "Asset": None,
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 2",
                "Task Result": None,
                "Ticket Status": "Closed",
            }
        ]
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows
            },
            'response_topic': response_topic,
        }
        expected_predictions = {
            "body":
                [
                    {
                        "assetId": "some_serial_number",
                        "predictions": [
                            {
                                "name": "Some action",
                                "probability": 0.9484384655952454
                            },
                        ]
                    }
                ],
            "status": 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value=expected_predictions)

        t7_kre_repository = Mock()
        t7_kre_repository.get_prediction = Mock(return_value=expected_predictions)

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository, t7_kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        prediction_action._t7_repository.get_prediction.assert_called_once_with(ticket_id)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_predictions,
            }
        )
        prediction_action._t7_kre_repository.get_prediction.assert_called_once_with(ticket_id, ticket_rows)

        assert logger.info.call_count == 2

    @pytest.mark.asyncio
    async def get_prediction_kre_non_200_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        request_id = 123
        ticket_id = 321
        ticket_rows = [
            {
                "Asset": "asset1",
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 1",
                "Task Result": None,
                "Ticket Status": "Closed",
            },
            {
                "Asset": None,
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 2",
                "Task Result": None,
                "Ticket Status": "Closed",
            }
        ]
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows
            },
            'response_topic': response_topic,
        }
        expected_predictions = {
            "body":
                [
                    {
                        "assetId": "some_serial_number",
                        "predictions": [
                            {
                                "name": "Some action",
                                "probability": 0.9484384655952454
                            },
                        ]
                    }
                ],
            "status": 200
        }

        kre_get_prediction_response = {
            "body": "error",
            "status": 500
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value=expected_predictions)

        t7_kre_repository = Mock()
        t7_kre_repository.get_prediction = Mock(return_value=kre_get_prediction_response)

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository, t7_kre_repository)
        await prediction_action.get_prediction(msg_published_in_topic)

        prediction_action._t7_repository.get_prediction.assert_called_once_with(ticket_id)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_predictions,
            }
        )
        prediction_action._t7_kre_repository.get_prediction.assert_called_once_with(ticket_id, ticket_rows)

        assert logger.info.call_count == 1
        assert logger.info.call_count == 1
        logger.error.assert_called_once_with((
            f"ERROR on KRE get prediction for ticket_id[{ticket_id}]:"
            f"Body: {kre_get_prediction_response['body']}, Status: {kre_get_prediction_response['status']}"
        ))
