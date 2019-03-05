import requests
import json


class SlackClient:
    _url = None
    _config = None

    def __init__(self, config):
        self._config = config.SLACK_CONFIG
        self._url = self._config['webhook']

    def send_to_slack(self, msg):
        header = 'https://'
        response = None
        if header in self._url:
            response = requests.post(self._url, data=json.dumps(msg))
        else:
            print("Invalid URL")

        # if an error arises prints out the status code
        if response.status_code != 200:
            print('HTTP error', response.status_code)
            return response
        else:
            print(str(msg))
            return response
