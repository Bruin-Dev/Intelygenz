from urllib.parse import urlencode
from base64 import b64encode

import requests


class TeleStaxClient:

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger

        user_and_pass_bytes = bytes(
            f"{self._config.TELESTAX_CONFIG['account_sid']}:"
            f"{self._config.TELESTAX_CONFIG['auth_token']}"
            'utf-8'
        )
        user_and_pass = b64encode(user_and_pass_bytes).decode("ascii")
        self._headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {user_and_pass}',
            'Accept': 'text/plain'
        }

    def _get_sms_data(self, msg, sms_from, sms_to):
        sms_data = urlencode({
            'From': sms_from,
            'To': sms_to,
            'Body': msg['sms_data']
            # ,'StatusCallback': 'http://status.callback.url'
        })
        return sms_data

    def send_to_sms(self, msg):
        try:
            sms_from = self._config.TELESTAX_CONFIG['from']
            for i, sms_to in enumerate(self._config.TELESTAX_CONFIG['to']):
                sms_data = self._get_sms_data(msg, sms_from, sms_to)
                response = requests.request("POST", self._config.TELESTAX_CONFIG['url'],
                                            headers=self._headers, data=sms_data)
                if response.status_code not in range(200, 300):
                    self._logger.error(f"Error: SMS {i} "
                                       f"not sent: {response.json()}")
                self._logger.info(f"Success: SMS {i} sent!")
            return 200
        except Exception as ex:
            self._logger.exception(f'Error: SMS not sent, exception: {ex}')
            return 500
