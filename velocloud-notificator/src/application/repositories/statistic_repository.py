from ast import literal_eval
import logging
import sys
from igz.packages.Logger.logger_client import LoggerClient


class StatisticRepository:

    _config = None
    _statistic_client = None
    _activation_key = None
    _edge_state = None
    formatter = logging.Formatter('%(asctime)s: %(module)s: %(message)s')
    error_log = LoggerClient().create_logger('stats_repo_KO', sys.stderr, formatter, logging.ERROR)

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
        self._activation_key = msg_dict['activationKey']
        self._edge_state = msg_dict['edgeState']
        # relevant_info = {}
        # relevant_info['activationState'] = msg['activationState']
        # relevant_info['edgeState'] = msg['edgeState']
        # relevant_info['serviceState'] = msg['serviceState']
        if getattr(self._statistic_client, 'store_edge') is None:
            self.error_log.error(f'The object {self._statistic_client} has no method named store_edge')
            return None
        self._statistic_client.store_edge(self._activation_key, self._edge_state)
