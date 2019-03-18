from ast import literal_eval


class StatisticRepository:

    _config = None
    _statistic_client = None
    _activation_key = None
    _edge_state = None
    _logger = None

    def __init__(self, config, statistic_client, logger):
        self._config = config
        self._statistic_client = statistic_client
        self._logger = logger

    def send_to_stats_client(self, msg):
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        self._activation_key = msg_dict['activationKey']
        self._edge_state = msg_dict['edgeState']
        if getattr(self._statistic_client, 'store_edge') is None:
            self._logger.error(f'The object {self._statistic_client} has no method named store_edge')
            return None
        self._statistic_client.store_edge(self._activation_key, self._edge_state)
