class EmailRepository:
    def __init__(self, config, email_client, logger):
        self._config = config
        self._email_client = email_client
        self._logger = logger

    def send_to_email(self, msg):
        status = self._email_client.send_to_email(msg)
        return status
