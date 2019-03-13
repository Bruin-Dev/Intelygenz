import requests
import json
import logging
import sys
from igz.packages.Logger.logger_client import LoggerClient


class SlackClient:
    _url = None
    _config = None

    formatter = logging.Formatter('%(asctime)s: %(module)s: %(message)s')

    info_log = LoggerClient().create_logger('slack_client_OK', sys.stdout, formatter, logging.INFO)
    error_log = LoggerClient().create_logger('slack_client_KO', sys.stderr, formatter, logging.ERROR)

    def __init__(self, config):
        self._config = config.SLACK_CONFIG
        self._url = self._config['webhook'][0]

    def send_to_slack(self, msg):
        header = 'https://'
        response = None
        if header in self._url:
            response = requests.post(self._url, data=json.dumps(msg))
        else:
            self.error_log.error("Invalid URL")
            return response

        # if an error arises prints out the status code
        if response.status_code != 200:
            self.error_log.error('HTTP error ' + str(response.status_code))
            return 'HTTP error ' + str(response.status_code)
        else:
            self.info_log.info(str(msg) + 'sent with a status code of ' + str(response.status_code))
            return str(msg) + 'sent with status code of ' + str(response.status_code)
