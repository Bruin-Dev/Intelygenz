from unittest.mock import Mock

import pytest
from application.actions.get_prediction import GetPrediction
from asynctest import CoroutineMock


class TestGetPrediction:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        t7_kre_repository = Mock()

        prediction = GetPrediction(logger, config, event_bus, t7_kre_repository)

        assert prediction._config == config
        assert prediction._logger == logger
        assert prediction._event_bus == event_bus
        assert prediction._t7_kre_repository == t7_kre_repository

    @pytest.mark.parametrize(
        'body_in_topic', [
            None,
            ({'some-key': 'some-data'}),
            ({'ticket_id': 12345}),
            ({'ticket_rows': [{'asset': '7627627'}]}),
        ], ids=[
            'without_body',
            'without_params',
            'without_ticket_rows',
            'without_ticket_id'
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
        logger.info = Mock()
        logger.error = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_kre_repository = Mock()
        t7_kre_repository.get_prediction = Mock()

        prediction_action = GetPrediction(logger, config, event_bus, t7_kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        logger.error.assert_called_once()
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": {"ticket_id", "ticket_rows", "assets_to_predict"}..} '
                        'in the request',
                'status': 400,
            }
        )
        prediction_action._t7_kre_repository.get_prediction.assert_not_called()
        logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def get_prediction_test(self):
        config = Mock()
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        request_id = 123
        ticket_id = 321
        assets_to_predict = ["asset1"]
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
                'ticket_rows': ticket_rows,
                'assets_to_predict': assets_to_predict
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

        t7_kre_repository = Mock()
        t7_kre_repository.get_prediction = Mock(return_value=expected_predictions)

        prediction_action = GetPrediction(logger, config, event_bus, t7_kre_repository)

        await prediction_action.get_prediction(msg_published_in_topic)

        logger.error.assert_not_called()
        prediction_action._t7_kre_repository.get_prediction.assert_called_once_with(
            ticket_id, ticket_rows, assets_to_predict
        )
        prediction_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **expected_predictions,
            }
        )
        logger.info.assert_called_once()
