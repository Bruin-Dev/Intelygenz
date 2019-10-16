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
    async def get_prediction_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()

        request_id = 123
        ticket_id = 321
        response_topic = 't7.prediction.response'
        msg_published_in_topic = {
            'request_id': request_id,
            'ticket_id': ticket_id,
            'response_topic': response_topic,
        }
        expected_predictions = ['prediction-1', 'prediction-2', 'prediction-3']

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value=expected_predictions)

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository)
        await prediction_action.get_prediction(json.dumps(msg_published_in_topic))

        prediction_action._t7_repository.get_prediction.assert_called_once_with(ticket_id)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            json.dumps({
                'request_id': request_id,
                'prediction': expected_predictions,
                'status': 200,
            })
        )
        logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def get_predication_with_bad_status_code_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()

        request_id = 123
        ticket_id = 321
        response_topic = 't7.prediction.response'
        msg_published_in_topic = {
            'request_id': request_id,
            'ticket_id': ticket_id,
            'response_topic': response_topic,
        }
        expected_predictions = None

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value=expected_predictions)

        prediction_action = GetPrediction(logger, config, event_bus, t7_repository)
        await prediction_action.get_prediction(json.dumps(msg_published_in_topic))

        prediction_action._t7_repository.get_prediction.assert_called_once_with(ticket_id)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            json.dumps({
                'request_id': request_id,
                'prediction': expected_predictions,
                'status': 500,
            })
        )
        logger.info.assert_called_once()
