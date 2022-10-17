import base64
from email.mime.image import MIMEImage
from unittest.mock import Mock, patch

import application
from application.clients.email_client import EmailClient
from config import testconfig as config


class TestEmailClient:
    def instantiation_test(self):
        test_client = EmailClient(config)

        assert test_client._config is config

    def email_login_test(self):
        test_client = EmailClient(config)

        with patch.object(application.clients.email_client.smtplib, "SMTP"):
            test_client.email_login()

            test_client._email_server.ehlo.assert_called_once()
            test_client._email_server.starttls.assert_called_once()
            test_client._email_server.login.assert_called_once_with(
                test_client._config.EMAIL_CONFIG["sender_email"],
                test_client._config.EMAIL_CONFIG["password"],
            )

    def send_to_email_test(self):
        mock_image = base64.b64encode(open("src/templates/images/logo.png", "rb").read()).decode("utf-8")
        test_msg = {
            "subject": "subject",
            "message": "message",
            "recipient": "fake@gmail.com",
            "images": [{"name": "foo", "data": mock_image}],
            "attachments": [],
            "text": "Some email test",
            "html": "<div>Some message html</div>",
        }

        with patch.object(application.clients.email_client, "MIMEImage", wraps=MIMEImage) as mock:
            test_client = EmailClient(config)
            test_client.email_login = Mock()
            test_client._email_server = Mock()
            test_client._email_server.quit = Mock()
            test_client._email_server.sendmail = Mock()

            status = test_client.send_to_email(test_msg)
            mock.assert_called_with(base64.b64decode(mock_image.encode()))

        assert status == 200

        # Checking the MIME attachment can be too much verbose, so we cannot
        # use assert_called_with here
        test_client._email_server.sendmail.assert_called_once()
        assert test_client._email_server.sendmail.call_args[0][0] == test_client._config.EMAIL_CONFIG["sender_email"]
        assert test_client._email_server.sendmail.call_args[0][1] == test_msg["recipient"]
        assert isinstance(test_client._email_server.sendmail.call_args[0][2], str)
        test_client._email_server.quit.assert_called_once()

    def send_to_email_with_failure_test(self):
        test_msg = {}

        test_client = EmailClient(config)
        test_client._email_server = Mock()
        test_client._email_server.sendmail = Mock(side_effect=Exception)

        status = test_client.send_to_email(test_msg)

        assert status == 500
