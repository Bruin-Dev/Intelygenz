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
    async def get_predication_ok_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value='Some list of predictions')
        msg = {'request_id': 123, 'response_topic': 't7.prediction.response', 'ticket_id': 321}
        prediction = GetPrediction(logger, config, event_bus, t7_repository)
        await prediction.get_prediction(json.dumps(msg))
        assert t7_repository.get_prediction.called
        assert t7_repository.get_prediction.call_args[0][0] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'prediction': 'Some list of predictions',
                                                                        'status': 200})
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_predication_ko_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        t7_repository = Mock()
        t7_repository.get_prediction = Mock(return_value=None)
        msg = {'request_id': 123, 'response_topic': 't7.prediction.response', 'ticket_id': 321}
        prediction = GetPrediction(logger, config, event_bus, t7_repository)
        await prediction.get_prediction(json.dumps(msg))
        assert t7_repository.get_prediction.called
        assert t7_repository.get_prediction.call_args[0][0] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'prediction': None,
                                                                        'status': 500})
        assert logger.info.called
