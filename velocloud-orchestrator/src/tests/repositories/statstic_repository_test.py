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

    def store_stats_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_dict_msg = {'edges': {'activationKey': 1234, 'edgeState': 'CONNECTED'},
                         'links': [{'linkId': 4321, 'link':
                                   {'state': 'STABLE'}}]}
        test_repo._statistic_client.store_edge = Mock()
        test_repo._statistic_client.store_link = Mock()
        test_repo.store_stats(test_dict_msg)
        assert test_repo._statistic_client.store_edge.called
        assert test_repo._statistic_client.store_link.called
        assert test_repo._statistic_client.store_edge.call_args[0][0] == 1234
        assert test_repo._statistic_client.store_edge.call_args[0][1] == 'CONNECTED'
        assert test_repo._statistic_client.store_link.call_args[0][0] == 4321
        assert test_repo._statistic_client.store_link.call_args[0][1] == 'STABLE'

    def store_stats_no_links_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_dict_msg = {'edges': {'activationKey': 1234, 'edgeState': 'CONNECTED'},
                         'links': []}
        test_repo._statistic_client.store_edge = Mock()
        test_repo._statistic_client.store_link = Mock()
        test_repo.store_stats(test_dict_msg)
        assert test_repo._statistic_client.store_edge.called
        assert test_repo._statistic_client.store_edge.call_args[0][0] == 1234
        assert test_repo._statistic_client.store_edge.call_args[0][1] == 'CONNECTED'
        assert test_repo._statistic_client.store_link.called is False
