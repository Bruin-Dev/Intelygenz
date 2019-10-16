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
        expected_predictions = ['prediction-1', 'prediction-2', 'prediction-3']

        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value=expected_predictions)

        t7_repository = T7Repository(logger, t7_client)
        predictions = t7_repository.get_prediction(ticket_id=ticket_id)

        t7_repository._t7_client.get_prediction.assert_called_once_with(ticket_id)
        assert predictions == expected_predictions
