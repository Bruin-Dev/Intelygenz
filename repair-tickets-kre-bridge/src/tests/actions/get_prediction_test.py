from unittest.mock import Mock

import pytest
from application.actions.get_prediction import GetPrediction
from asynctest import CoroutineMock


class TestGetPrediction:
    valid_email_data = {
        "email": {
            "email_id": 123,
            "body": "test body",
            "subject": "test subject"
        }
    }

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        prediction = GetPrediction(logger, config, event_bus, kre_repository)

        assert prediction._config == config
        assert prediction._logger == logger
        assert prediction._event_bus == event_bus
        assert prediction._kre_repository == kre_repository

    @pytest.mark.parametrize(
        'body_in_topic', [
            None,
            ({'some-key': 'some-data'}),
        ], ids=[
            'without_body',
            'without_params',
        ]
    )
    @pytest.mark.asyncio
    async def get_prediction_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': body_in_topic
        }
        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.get_prediction = CoroutineMock()

        prediction_action = GetPrediction(logger, config, event_bus, kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        logger.error.assert_called_once()
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": { "email": {"email_id", "subject", ...}}} in the request',
                'status': 400,
            }
        )
        prediction_action._kre_repository.get_prediction.assert_not_awaited()
        logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def get_prediction_test(self):
        config = Mock()
        logger = Mock()

        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': self.valid_email_data,
            'response_topic': response_topic,
        }
        expected_prediction = {
            "body": {
                "email_id": 123,
                "prediction": [
                    {"tag_id": "1002", "probability": 0.67},
                    {"tag_id": "1004", "probability": 0.27},
                    {"tag_id": "1001", "probability": 0.03},
                ]
            },
            "status": 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.get_prediction = CoroutineMock(return_value=expected_prediction)

        prediction_action = GetPrediction(logger, config, event_bus, kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        logger.error.assert_not_called()
        prediction_action._kre_repository.get_prediction.assert_awaited_once_with(self.valid_email_data)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_prediction,
            }
        )
        logger.info.assert_called_once()
