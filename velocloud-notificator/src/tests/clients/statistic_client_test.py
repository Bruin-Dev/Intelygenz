from application.clients.statistic_client import StatisticClient
from unittest.mock import Mock
from config import testconfig as config


class TestStatisticClient:

    def instantiation_test(self):
        test_client = StatisticClient(config)
        assert test_client._config == config
        assert test_client._edge_dictionary == {}
        assert test_client._link_dictionary == {}

    def store_edge_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        test_key = 54321
        test_state = "OFFLINE"
        test_client.store_edge(test_key, test_state)
        assert test_client._edge_dictionary == {test_key: test_state}
        test_key = 12345
        test_state = "CONNECTED"
        test_client.store_edge(test_key, test_state)
        assert test_client._edge_dictionary == {54321: "OFFLINE", test_key: test_state}
        new_state = "NEVER_ACTIVATED"
        test_client.store_edge(test_key, new_state)
        assert test_client._edge_dictionary == {54321: "OFFLINE", test_key: new_state}

    def store_link_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        test_id = 54321
        test_state = "STABLE"
        test_client.store_link(test_id, test_state)
        assert test_client._link_dictionary == {test_id: test_state}
        test_id = 12345
        test_state = "OFFLINE"
        test_client.store_link(test_id, test_state)
        assert test_client._link_dictionary == {54321: "STABLE", test_id: test_state}
        new_state = "NEVER_ACTIVATED"
        test_client.store_link(test_id, new_state)
        assert test_client._link_dictionary == {54321: "STABLE", test_id: new_state}

    def create_statistics_dictionary_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        test_dict = {'someId': 'OFFLINE', 'anotherId': 'NEVER_ACTIVATED', 'testID': 'OFFLINE'}
        test_stats_dict = test_client.create_statistics_dictionary(test_dict)
        assert test_stats_dict == {'OFFLINE': 2, 'NEVER_ACTIVATED': 1}

    def get_statistics_test(self):
        test_client = StatisticClient(config)
        test_client.clear_dictionaries()
        time = config.SLACK_CONFIG['time']
        msg1 = test_client.get_statistics(time)
        assert msg1 is None
        test_edge_dict = {'someId': 'OFFLINE', 'anotherId': 'NEVER_ACTIVATED', 'testID': 'OFFLINE'}
        test_client._edge_dictionary = test_edge_dict
        time = config.SLACK_CONFIG['time']
        msg2_results = f"Edge Status Counters (last {time} minutes)\nOFFLINE: 2\nNEVER_ACTIVATED: 1\nTotal: 3\n"
        msg2 = test_client.get_statistics(time)
        assert msg2 == msg2_results
        test_link_dict = {'someId': 'OFFLINE', 'anotherId': 'NEVER_ACTIVATED', 'testID': 'OFFLINE'}
        test_client._link_dictionary = test_link_dict
        msg3_results = msg2_results + f"Link Status Counters (last {time} minutes)" \
            "\nOFFLINE: 2\nNEVER_ACTIVATED: 1\nTotal: 3"
        msg3 = test_client.get_statistics(time)
        assert msg3 == msg3_results

    def clear_dictionaries_test(self):
        test_client = StatisticClient(config)
        test_dict = {"TestId": "CONNECTED"}
        test_client._edge_dictionary = test_dict
        test_client._link_dictionary = test_dict
        test_client.clear_dictionaries()
        assert test_client._edge_dictionary is not test_dict
        assert test_client._link_dictionary is not test_dict
        assert test_client._edge_dictionary == {}
        assert test_client._link_dictionary == {}
