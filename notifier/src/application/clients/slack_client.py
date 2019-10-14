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
            error_msg = f'ERROR - Request returned HTTP {response.status_code}'
            self._logger.error(error_msg)
            return error_msg
        else:
            info_msg = f'Request with message {str(msg)} returned a response with status code {response.status_code}'
            self._logger.info(info_msg)
            return info_msg
