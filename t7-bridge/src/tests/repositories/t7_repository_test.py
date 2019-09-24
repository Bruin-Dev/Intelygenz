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
        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value='Some list of predictions')
        t7_repository = T7Repository(logger, t7_client)
        prediction = t7_repository.get_prediction(123)
        assert t7_client.get_prediction.called
        assert t7_client.get_prediction.call_args[0][0] == 123
        assert prediction == 'Some list of predictions'
