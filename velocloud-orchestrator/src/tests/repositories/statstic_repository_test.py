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

    def send_to_stats_client_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_dict_msg = {'edges': {'activationKey': 1234, 'edgeState': 'CONNECTED'},
                         'links': [{'linkId': 4321, 'link':
                                   {'state': 'STABLE'}}]}
        test_repo._statistic_client.store_edge = Mock()
        test_repo._statistic_client.store_link = Mock()
        test_repo.send_to_stats_client(test_dict_msg)
        assert test_repo._activation_key == 1234
        assert test_repo._edge_state == 'CONNECTED'
        assert test_repo._link_id == 4321
        assert test_repo._link_state == 'STABLE'
        assert test_repo._statistic_client.store_link.called
        assert test_repo._statistic_client.store_edge.called

    def send_to_stats_client_no_links_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = StatisticRepository(config, mock_client, mock_logger)
        test_dict_msg = {'edges': {'activationKey': 1234, 'edgeState': 'CONNECTED'},
                         'links': []}
        test_repo._statistic_client.store_edge = Mock()
        test_repo._statistic_client.store_link = Mock()
        test_repo.send_to_stats_client(test_dict_msg)
        assert test_repo._activation_key == 1234
        assert test_repo._edge_state == 'CONNECTED'
        assert test_repo._link_id is None
        assert test_repo._link_state is None
        assert test_repo._statistic_client.store_link.called is False
        assert test_repo._statistic_client.store_edge.called
