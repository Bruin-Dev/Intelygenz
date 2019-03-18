class StatisticClient:
    _config = None
    _edge_dictionary = {}
    _stats_dictionary = {}

    def __init__(self, config):
        self._config = config

    def store_edge(self, activation_key, edge_state):
        self._edge_dictionary[activation_key] = edge_state
        self.store_statistics_dictionary(edge_state)

    def store_statistics_dictionary(self, edge_state):
        if edge_state in self._stats_dictionary:
            self._stats_dictionary[edge_state] += 1
        else:
            self._stats_dictionary[edge_state] = 1

    def get_statistics(self, time):

        if self._stats_dictionary:
            msg = "Edge Status Counters (last %d minutes)\n" % (time)
            for status in self._stats_dictionary:
                msg = msg + status + ": " + str(self._stats_dictionary[status]) + "\n"
            mysum = sum(self._stats_dictionary.values())
            msg = msg + "Total: " + str(mysum)
        else:
            msg = None
        return msg

    def clear_dictionaries(self):
        self._edge_dictionary = {}
        self._stats_dictionary = {}
