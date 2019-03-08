class StatisticClient:
    _config = None
    _edge_dictionary = {}
    _stats_dictionary = {}

    def __init__(self, config):
        self._config = config

    # stores the data gained from the stats repo in a
    # a dictionary of all edges and their relevant infos
    # format { key = device_id : value = dictionary of relevant_info }
    # also overwrite if device_id already exists
    def store_edge(self, activation_key, edge_state):
        self._edge_dictionary[activation_key] = edge_state
        # Once activation key and edge state has been added to the edge dict
        # move that info in the stat_dictionary so that can be updated
        # at the same rate as the edge dictionary is updated
        self.store_statistics_dictionary(edge_state)

    # If stat exists in dictionary add 1 to current number
    # else add stat and make it equal one
    # store in _stats_dictionary
    # future format { key = which state (activation, edge, or service) :
    #                 { key = what state : value : amount of occurence}}
    # starter format edge only { key = what state : value : amount of occurrence}
    def store_statistics_dictionary(self, edge_state):
        if edge_state in self._stats_dictionary:
            self._stats_dictionary[edge_state] += 1
        else:
            self._stats_dictionary[edge_state] = 1

    # goes through _stats_dictionary and returns
    # a msg to be formatted and sent to slack
    # in the format of a list
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

    # clear the dictionaries in order to restart after the minute
    def clear_dictionaries(self):
        self._edge_dictionary = {}
        self._stats_dictionary = {}
