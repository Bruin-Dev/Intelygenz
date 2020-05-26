class TeleStaxRepository:

    def __init__(self, config, telestax_client, logger):
        self._config = config
        self._telestax_client = telestax_client
        self._logger = logger

    def send_to_email(self, msg):
        status = self.telestax_client.send_to_sms(msg)
        return status
