from ast import literal_eval


class StatisticRepository:

    _config = None
    _statistic_client = None
    _activation_key = None
    _edge_state = None
    _logger = None
    _link_id = None
    _link_state = None

    def __init__(self, config, statistic_client, logger):
        self._config = config
        self._statistic_client = statistic_client
        self._logger = logger

    def send_to_stats_client(self, msg):
        decoded_msg = msg.decode('utf-8')
        decoded_msg = decoded_msg.replace('datetime.datetime', '')
        decoded_msg = decoded_msg.replace(', tzinfo=tzlocal()', '')
        decoded_msg = decoded_msg.replace(', tzinfo=tzutc()', '')
        msg_dict = literal_eval(decoded_msg)
        for links in msg_dict['links']:
            links['link'].pop('created', None)
            links['link'].pop('lastActive', None)
            links['link'].pop('lastEvent', None)
            links['link'].pop('modified', None)
        edge_msg_dict = msg_dict["edges"]
        link_msg_dict = msg_dict["links"]
        self._activation_key = edge_msg_dict['activationKey']
        self._edge_state = edge_msg_dict['edgeState']
        if hasattr(self._statistic_client, 'store_edge') is False:
            self._logger.error(f'The object {self._statistic_client} has no method named store_edge')
            return None
        self._statistic_client.store_edge(self._activation_key, self._edge_state)

        if link_msg_dict:
            for links in link_msg_dict:
                self._link_id = links['linkId']
                self._link_state = links['link']['state']
            if hasattr(self._statistic_client, 'store_link') is False:
                self._logger.error(f'The object {self._statistic_client} has no method named store_link')
                return None
            self._statistic_client.store_link(self._link_id, self._link_state)
