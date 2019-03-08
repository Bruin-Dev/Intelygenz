from unittest.mock import Mock
from config import testconfig as config
from application.repositories.statistic_repository import StatisticRepository


class TestStatisticRepository:

    def instantiation_test(self):
        mock_client = Mock()
        test_repo = StatisticRepository(config, mock_client)
        assert test_repo._config == config

    def send_to_stats_client_test(self):
        mock_client = Mock()
        test_repo = StatisticRepository(config, mock_client)
        test_dict_msg = b"{'activationKey': 1234 , 'edgeState': 'CONNECTED'  } "
        test_repo._statistic_client.store_edge = Mock()
        test_repo.send_to_stats_client(test_dict_msg)
        assert test_repo._activation_key == 1234
        assert test_repo._edge_state == 'CONNECTED'
        assert test_repo._statistic_client.store_edge.called
