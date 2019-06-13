import smtplib


class EmailClient:

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger
        self.email_login()

    def email_login(self):
        try:
            self._email_server = smtplib.SMTP('smtp.gmail.com:587')
            self._email_server.ehlo()
            self._email_server.starttls()
            self._email_server.login(self._config.EMAIL_CONFIG['sender_email'], self._config.EMAIL_CONFIG['password'])
        except Exception:
            self._logger.exception('Error: Could not login')

    def send_to_email(self, msg):
        try:
            self._email_server.sendmail(self._config.EMAIL_CONFIG['sender_email'],
                                        self._config.EMAIL_CONFIG['recipient_email'],
                                        msg)
            self._logger.info("Success: Email sent!")
            return 200
        except Exception:
            self._logger.exception('Error: Email not sent')
            return 500
