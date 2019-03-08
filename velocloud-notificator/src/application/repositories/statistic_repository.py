from ast import literal_eval


class StatisticRepository:

    _config = None
    _statistic_client = None

    def __init__(self, config, statistic_client):
        self._config = config
        self._statistic_client = statistic_client

    def send_to_stats_client(self, msg):
        # break up message
        # decode the msg from byte form
        # to string then convert to dict
        # to allow us to
        # grab activation id as the key
        # puts service state, activation state, and edge state in a
        # relevant_info dictionary
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        if msg_dict['activationKey'] is not None:
            activation_key = msg_dict['activationKey']
        else:
            activation_key = 'None'
        edge_state = msg_dict['edgeState']
        # relevant_info = {}
        # relevant_info['activationState'] = msg['activationState']
        # relevant_info['edgeState'] = msg['edgeState']
        # relevant_info['serviceState'] = msg['serviceState']
        self._statistic_client.store_edge(activation_key, edge_state)
