from application.clients.statistic_client import StatisticClient
from unittest.mock import Mock
from config import testconfig as config


class TestStatisticClient:

    def instantiation_test(self):
        test_client = StatisticClient(config)
        assert test_client._config == config
        assert test_client._edge_dictionary == {}
        assert test_client._edge_stats_dictionary == {}

    def store_edge_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        test_key = 54321
        test_state = "OFFLINE"
        test_client.store_statistics_dictionary = Mock()
        test_client.store_edge(test_key, test_state)
        assert test_client._edge_dictionary == {test_key: test_state}
        assert test_client.store_statistics_dictionary.called
        test_key = 12345
        test_state = "CONNECTED"
        test_client.store_edge(test_key, test_state)
        assert test_client._edge_dictionary == {54321: "OFFLINE", test_key: test_state}
        new_state = "NEVER_ACTIVATED"
        test_client.store_edge(test_key, new_state)
        assert test_client._edge_dictionary == {54321: "OFFLINE", test_key: new_state}

    def store_edge_statistics_dictionary_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        test_state = "OFFLINE"
        new_state = "NEVER_ACTIVATED"
        test_client.store_edge_statistics_dictionary(test_state)
        test_client.store_edge_statistics_dictionary(test_state)
        test_client.store_edge_statistics_dictionary(new_state)
        assert test_client._edge_stats_dictionary == {test_state: 2, new_state: 1}

    def get_statistics_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        time = config.SLACK_CONFIG['time']
        msg1 = test_client.get_statistics(time)
        assert msg1 is None
        test_dict = {"OFFLINE": 2, "NEVER_ACTIVATED": 1}
        test_client._stats_dictionary = test_dict
        msg2 = test_client.get_statistics(time)
        assert msg2 == "Edge Status Counters (last 60 minutes)\nOFFLINE: 2\nNEVER_ACTIVATED: 1\nTotal: 3"

    def clear_dictionaries_test(self):
        test_client = StatisticClient(config)
        test_dict = {"TestId": "CONNECTED"}
        test_client._edge_dictionary = test_dict
        test_client._stats_dictionary = test_dict
        test_client.clear_dictionaries()
        assert test_client._edge_dictionary is not test_dict
        assert test_client._edge_stats_dictionary is not test_dict
        assert test_client._edge_dictionary == {}
        assert test_client._edge_stats_dictionary == {}
