from unittest.mock import Mock, patch

import application
from application.clients.email_client import EmailClient
from config import testconfig as config


class TestEmailClient:
    def instantiation_test(self, email_client, logger):
        assert email_client._config is config
        assert email_client._logger is logger

    def email_login_test(self, email_client):
        with patch.object(application.clients.email_client.smtplib, "SMTP"):
            email_client.email_login()

            email_client._email_server.ehlo.assert_called_once()
            email_client._email_server.starttls.assert_called_once()
            email_client._email_server.login.assert_called_once_with(
                email_client._config.EMAIL_DELIVERY_CONFIG["email"],
                email_client._config.EMAIL_DELIVERY_CONFIG["password"],
            )

    def send_to_email_test(self, email_client):
        test_msg = {
            "subject": "subject",
            "message": "message",
            "recipient": "fake@gmail.com",
            "images": [],
            "attachments": [],
            "text": "Some email test",
            "html": "<div>Some message html</div>",
        }
        email_client.email_login = Mock()
        email_client._email_server = Mock()

        status = email_client.send_to_email(test_msg)

        email_client._logger.info.assert_called_once()
        assert status == 200

        # Checking the MIME attachment can be too much verbose, so we cannot
        # use assert_called_with here
        email_client._email_server.sendmail.assert_called_once()
        assert (
            email_client._email_server.sendmail.call_args[0][0] == email_client._config.EMAIL_DELIVERY_CONFIG["email"]
        )
        assert email_client._email_server.sendmail.call_args[0][1] == test_msg["recipient"].split(
            email_client.EMAIL_SEPARATOR
        )
        assert isinstance(email_client._email_server.sendmail.call_args[0][2], str)
        email_client._email_server.quit.assert_called_once()
        email_client._logger.exception.assert_not_called()

    def send_to_email_with_failure_test(self, email_client):
        test_msg = {}
        email_client._email_server = Mock()
        email_client._email_server.sendmail = Mock(side_effect=Exception)

        status = email_client.send_to_email(test_msg)

        assert status == 500
        email_client._logger.info.assert_not_called()
        email_client._logger.exception.assert_called_once()
