from unittest.mock import Mock

import pytest
from application.actions.save_prediction import SavePrediction
from asynctest import CoroutineMock


class TestSavePrediction:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        t7_repository = Mock()
        t7_kre_repository = Mock()

        automation_metrics = SavePrediction(logger, config, event_bus, t7_kre_repository)

        assert automation_metrics._config == config
        assert automation_metrics._logger == logger
        assert automation_metrics._event_bus == event_bus
        assert automation_metrics._t7_kre_repository == t7_kre_repository

    @pytest.mark.asyncio
    async def save_prediction_with_no_body_in_request_message_test(self):
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

        t7_kre_repository = Mock()
        t7_kre_repository.save_prediction = Mock()

        automation_metrics = SavePrediction(logger, config, event_bus, t7_kre_repository)

        await automation_metrics.save_prediction(msg_published_in_topic)

        t7_kre_repository.save_prediction.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': (
                    'You must specify {.."body": {"ticket_id", "ticket_rows", "predictions", "available_options" and'
                    ' "suggested_notes"}..} in the request'
                ),
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def save_prediction_with_no_ticket_id_and_available_options_in_request_message_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {
            "ticket_rows": [
                {
                    "Asset": "asset1",
                    "CallTicketID": 'ticket_id',
                    "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                    "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                    "Notes": "note 1",
                    "Task Result": None,
                    "Ticket Status": "Closed",
                },
                {
                    "Asset": None,
                    "CallTicketID": 'ticket_id',
                    "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                    "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                    "Notes": "note 2",
                    "Task Result": None,
                    "Ticket Status": "Closed",
                }
            ],
            "predictions": [
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
            "suggested_notes": [
                {'asset': 'VC1234567', 'suggested_note': 'This is TNBA note 1', 'details': None},
                {'asset': 'VC9999999', 'suggested_note': 'This is TNBA note 2', 'details': None}
            ],
        }

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_kre_repository = Mock()
        t7_kre_repository.save_prediction = Mock()

        automation_metrics = SavePrediction(logger, config, event_bus, t7_kre_repository)

        await automation_metrics.save_prediction(msg_published_in_topic)

        t7_kre_repository.save_prediction.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': (
                    'You must specify {.."body": {"ticket_id", "ticket_rows", "predictions", "available_options" and'
                    ' "suggested_notes"} in the request'
                ),
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def save_prediction_ok_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {
            "ticket_id": "ticket_id",
            "ticket_rows": [
                {
                    "Asset": "asset1",
                    "CallTicketID": 'ticket_id',
                    "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                    "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                    "Notes": "note 1",
                    "Task Result": None,
                    "Ticket Status": "Closed",
                },
                {
                    "Asset": None,
                    "CallTicketID": 'ticket_id',
                    "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                    "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                    "Notes": "note 2",
                    "Task Result": None,
                    "Ticket Status": "Closed",
                }
            ],
            "predictions": [
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
            "available_options": [
                {'asset': 'VC1234567', 'available_options': ['Request Completed']},
                {'asset': 'VC9999999', 'available_options': ['Request Completed']}
            ],
            "suggested_notes": [
                {'asset': 'VC1234567', 'suggested_note': 'This is TNBA note 1', 'details': None},
                {'asset': 'VC9999999', 'suggested_note': 'This is TNBA note 2', 'details': None}
            ],
        }

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()
        logger.info = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_kre_repository = Mock()
        t7_kre_repository.save_prediction = Mock(return_value={
            "status": 200
        })

        save_prediction = SavePrediction(logger, config, event_bus, t7_kre_repository)

        await save_prediction.save_prediction(msg_published_in_topic)

        t7_kre_repository.save_prediction.assert_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'Save prediction request for ticket_id[ticket_id] was sent to KRE',
                'status': 200
            }
        )

        assert logger.info.call_count == 2
