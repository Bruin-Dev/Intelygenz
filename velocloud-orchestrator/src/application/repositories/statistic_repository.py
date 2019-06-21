class StatisticRepository:

    def __init__(self, config, statistic_client, logger):
        self._config = config
        self._statistic_client = statistic_client
        self._logger = logger
        self._activation_key = None
        self._edge_state = None
        self._link_id = None
        self._link_state = None

    def send_to_stats_client(self, edge_info):
        edge_msg_dict = edge_info["edges"]
        link_msg_dict = edge_info["links"]
        self._activation_key = edge_msg_dict['activationKey']
        self._edge_state = edge_msg_dict['edgeState']
        self._statistic_client.store_edge(self._activation_key, self._edge_state)

        if link_msg_dict:
            for links in link_msg_dict:
                self._link_id = links['linkId']
                self._link_state = links['link']['state']
            self._statistic_client.store_link(self._link_id, self._link_state)
