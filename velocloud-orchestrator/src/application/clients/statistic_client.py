class StatisticClient:

    def __init__(self, config):
        self._config = config
        self. _edge_dictionary = {}
        self._link_dictionary = {}

    def store_edge(self, activation_key, edge_state):
        self._edge_dictionary[activation_key] = edge_state

    def store_link(self, link_id, link_state):
        self._link_dictionary[link_id] = link_state

    def _create_statistics_dictionary(self, dict):
        stats_dict = {}
        for key, value in dict.items():
            if value in stats_dict:
                stats_dict[value] += 1
            else:
                stats_dict[value] = 1
        return stats_dict

    def get_statistics(self):
        _edge_stats_dictionary = self._create_statistics_dictionary(self._edge_dictionary)
        _link_stats_dictionary = self._create_statistics_dictionary(self._link_dictionary)
        msg = ''
        if _edge_stats_dictionary:
            msg = "Failing Edge Status Counters \n"
            for status in _edge_stats_dictionary:
                msg = f'{msg}{str(status)}: {_edge_stats_dictionary[status]}\n'
            edgesum = sum(_edge_stats_dictionary.values())
            msg = f'{msg}Total: {str(edgesum)}\n'
        if _link_stats_dictionary:
            msg = msg + "Failing Edges' Link Status Counters \n"
            for status in _link_stats_dictionary:
                msg = f'{msg}{str(status)}: {_link_stats_dictionary[status]}\n'
            linksum = sum(_link_stats_dictionary.values())
            msg = f'{msg}Total: {str(linksum)}'
        if msg == '':
            msg = None
        return msg

    def clear_dictionaries(self):
        self._edge_dictionary = {}
        self._link_dictionary = {}
