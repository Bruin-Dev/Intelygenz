from unittest.mock import Mock
from config import testconfig as config
from application.repositories.statistic_repository import StatisticRepository


class TestStatisticRepository:

    def instantiation_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        assert test_repo._config == config
        assert test_repo._statistic_client == mock_client
        assert test_repo._logger is mock_logger

    def ok_send_to_stats_client_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_dict_msg = b"{'activationKey': 1234 , 'edgeState': 'CONNECTED'  } "
        test_repo._statistic_client.store_edge = Mock()
        test_repo.send_to_stats_client(test_dict_msg)
        assert test_repo._activation_key == 1234
        assert test_repo._edge_state == 'CONNECTED'
        assert test_repo._statistic_client.store_edge.called

    def ko_send_to_stats_client_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_repo._logger.error = Mock()
        test_dict_msg = b"{'activationKey': 1234 , 'edgeState': 'CONNECTED'  } "
        test_repo._statistic_client.store_edge = None
        return_type = test_repo.send_to_stats_client(test_dict_msg)
        assert return_type is None
        assert test_repo._logger.error.called
