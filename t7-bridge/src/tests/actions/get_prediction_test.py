import json
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

        prediction = GetPrediction(logger, config, event_bus, t7_repository)

        assert prediction._config == config
        assert prediction._logger == logger
        assert prediction._event_bus == event_bus
        assert prediction._t7_repository == t7_repository

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

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository)
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

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock()

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository)
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
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': {
                'ticket_id': ticket_id
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

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository)
        await prediction_action.get_prediction(msg_published_in_topic)

        prediction_action._t7_repository.get_prediction.assert_called_once_with(ticket_id)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_predictions,
            }
        )
