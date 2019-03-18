import requests
import json


class SlackClient:
    _url = None
    _config = None
    _logger = None

    def __init__(self, config, logger):
        self._config = config.SLACK_CONFIG
        self._url = self._config['webhook'][0]
        self._logger = logger

    def send_to_slack(self, msg):
        header = 'https://'
        response = None
        if header in self._url:
            response = requests.post(self._url, data=json.dumps(msg))
        else:
            self._logger.error("Invalid URL")
            return response

        if response.status_code != 200:
            self._logger.error('HTTP error ' + str(response.status_code))
            return 'HTTP error ' + str(response.status_code)
        else:
            self._logger.info(str(msg) + ' sent with a status code of ' + str(response.status_code))
            return str(msg) + 'sent with status code of ' + str(response.status_code)
