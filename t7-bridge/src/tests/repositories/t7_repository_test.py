from unittest.mock import Mock

from application.repositories.t7_repository import T7Repository


class TestT7Repository:

    def instance_test(self):
        logger = Mock()
        t7_client = Mock()

        t7_repository = T7Repository(logger, t7_client)

        assert t7_repository._logger is logger
        assert t7_repository._t7_client is t7_client

    def get_prediction_test(self):
        logger = Mock()
        ticket_id = 123
        raw_predictions = {
            "body": {
                "assets": [
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
                "requestId": "e676150a-73b9-412b-8207-ac2a3bbc9cbc"
            },
            "status_code": 200
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
            "status_code": 200
        }

        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value=raw_predictions)

        t7_repository = T7Repository(logger, t7_client)
        predictions = t7_repository.get_prediction(ticket_id=ticket_id)

        t7_repository._t7_client.get_prediction.assert_called_once_with(ticket_id)
        assert predictions == expected_predictions

    def get_prediction_not_200_test(self):
        logger = Mock()
        ticket_id = 123
        raw_predictions = {
            "body": {
                "Some error ocurred"
            },
            "status_code": 500
        }

        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value=raw_predictions)

        t7_repository = T7Repository(logger, t7_client)
        predictions = t7_repository.get_prediction(ticket_id=ticket_id)

        t7_repository._t7_client.get_prediction.assert_called_once_with(ticket_id)
        assert predictions == raw_predictions
