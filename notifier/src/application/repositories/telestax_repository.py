class TeleStaxRepository:

    def __init__(self, config, telestax_client, logger):
        self._config = config
        self._telestax_client = telestax_client
        self._logger = logger

    def send_to_sms(self, msg, sms_to):
        status = self._telestax_client.send_to_sms(msg, sms_to)
        return status
