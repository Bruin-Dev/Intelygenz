from unittest.mock import Mock

import pytest
from application.actions.get_email_inference import GetInference
from asynctest import CoroutineMock


class TestGetInference:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        prediction = GetInference(logger, config, event_bus, kre_repository)

        assert prediction._config == config
        assert prediction._logger == logger
        assert prediction._event_bus == event_bus
        assert prediction._kre_repository == kre_repository

    @pytest.mark.parametrize(
        'body_in_topic', [
            {},
            ({'some-key': 'some-data'}),
        ], ids=[
            'without_body',
            'without_params',
        ]
    )
    @pytest.mark.asyncio
    async def get_email_inference_error_400_test(self, body_in_topic):
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
        kre_repository.get_email_inference = CoroutineMock()

        prediction_action = GetInference(logger, config, event_bus, kre_repository)

        await prediction_action.get_email_inference(msg_published_in_topic)

        logger.error.assert_called_once()
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": { "email": {"email_id", "subject", ...}}} in the request',
                'status': 400,
            }
        )
        prediction_action._kre_repository.get_email_inference.assert_not_awaited()
        logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def get_email_inference_test(self, make_email, make_inference_request_payload, make_inference_data):
        config = Mock()
        logger = Mock()

        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        email = make_email(email_id="1234")
        request_body = make_inference_request_payload(email_data=email)
        msg_published_in_topic = {
            'request_id': request_id,
            'body': request_body,
            'response_topic': response_topic,
        }
        expected_prediction = {
            'status': 200,
            'body': make_inference_data()
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.get_email_inference = CoroutineMock(return_value=expected_prediction)

        prediction_action = GetInference(logger, config, event_bus, kre_repository)

        await prediction_action.get_email_inference(msg_published_in_topic)

        prediction_action._kre_repository.get_email_inference.assert_awaited_once_with(request_body)
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_prediction,
            }
        )
        logger.info.assert_called_once()
