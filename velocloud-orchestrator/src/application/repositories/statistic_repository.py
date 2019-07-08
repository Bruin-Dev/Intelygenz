class StatisticRepository:

    def __init__(self, config, statistic_client, logger):
        self._config = config
        self._statistic_client = statistic_client
        self._logger = logger

    def store_stats(self, edge_info):
        edge_msg_dict = edge_info["edges"]
        link_msg_dict = edge_info["links"]
        activation_key = edge_msg_dict['activationKey']
        edge_state = edge_msg_dict['edgeState']
        self._statistic_client.store_edge(activation_key, edge_state)

        if link_msg_dict:
            for links in link_msg_dict:
                link_id = links['linkId']
                link_state = links['link']['state']
                self._statistic_client.store_link(link_id, link_state)
