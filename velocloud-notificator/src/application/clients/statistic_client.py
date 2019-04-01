class StatisticClient:
    _config = None
    _edge_dictionary = {}
    _edge_stats_dictionary = {}
    _link_dictionary = {}
    _link_stats_dictionary = {}

    def __init__(self, config):
        self._config = config

    def store_edge(self, activation_key, edge_state):
        self._edge_dictionary[activation_key] = edge_state
        self.store_edge_statistics_dictionary(edge_state)

    def store_link(self, link_id, link_state):
        self._link_dictionary[link_id] = link_state
        self.store_link_statistics_dictionary(link_state)

    def store_edge_statistics_dictionary(self, edge_state):
        if edge_state in self._edge_stats_dictionary:
            self._edge_stats_dictionary[edge_state] += 1
        else:
            self._edge_stats_dictionary[edge_state] = 1

    def store_link_statistics_dictionary(self, link_state):
        if link_state in self._link_stats_dictionary:
            self._link_stats_dictionary[link_state] += 1
        else:
            self._link_stats_dictionary[link_state] = 1

    def get_statistics(self, time):
        msg = ''
        if self._edge_stats_dictionary:
            msg = "Edge Status Counters (last %d minutes)\n" % (time)
            for status in self._edge_stats_dictionary:
                msg = f'{msg}{str(status)}: {self._edge_stats_dictionary[status]}\n'
            edgesum = sum(self._edge_stats_dictionary.values())
            msg = f'{msg}Total: {str(edgesum)}\n'
        if self._link_stats_dictionary:
            msg = msg + "Link Status Counters (last %d minutes)\n" % (time)
            for status in self._link_stats_dictionary:
                msg = f'{msg}{str(status)}: {self._link_stats_dictionary[status]}\n'
            linksum = sum(self._link_stats_dictionary.values())
            msg = f'{msg}Total: {str(linksum)}'
        if msg == '':
            msg = None
        return msg

    def clear_dictionaries(self):
        self._edge_dictionary = {}
        self._edge_stats_dictionary = {}
        self._link_dictionary = {}
        self._link_stats_dictionary = {}
