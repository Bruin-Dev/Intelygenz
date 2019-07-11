import smtplib
from unittest.mock import Mock

import application
from application.clients.email_client import EmailClient

from config import testconfig as config


class TestEmailClient:

    def instantiation_test(self):
        mock_logger = Mock()
        application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        application.clients.email_client.smtplib.SMTP.starttls = Mock()
        application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        assert test_client._config == config
        assert test_client._logger == mock_logger

    def email_login_ok_test(self):
        mock_logger = Mock()
        mock_ehlo = application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        mock_starttls = application.clients.email_client.smtplib.SMTP.starttls = Mock()
        mock_login = application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        test_client.email_login()
        assert mock_ehlo.called
        assert mock_starttls.called
        mock_login.assert_called_with(test_client._config.EMAIL_CONFIG['sender_email'],
                                      test_client._config.EMAIL_CONFIG['password'], )

    def send_to_email_ok_test(self):
        test_msg = {"subject": "subject",
                    "message": "message",
                    "recipient": "fake@gmail.com",
                    "images": [],
                    "attachments": [],
                    "text": "Some email test",
                    "html": "<div>Some message html</div>"}
        mock_logger = Mock()
        application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        application.clients.email_client.smtplib.SMTP.starttls = Mock()
        application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        test_client.email_login = Mock()
        test_client._email_server = Mock()
        test_client._email_server.quit = Mock()
        test_client._email_server.sendmail = Mock()
        test_client._logger.info = Mock()
        test_client._logger.exception = Mock()
        status = test_client.send_to_email(test_msg)
        assert test_client._logger.info.called
        assert status == 200
        assert test_client._email_server.sendmail.called
        assert test_client._email_server.sendmail.call_args[0][0] == test_client._config.EMAIL_CONFIG['sender_email']
        assert test_client._email_server.sendmail.call_args[0][1] == test_msg["recipient"]
        assert isinstance(test_client._email_server.sendmail.call_args[0][2], str)
        assert test_client._logger.exception.called is False

    def send_to_email_ok_csv_not_provided_test(self):
        test_msg = {"subject": "subject",
                    "message": "message",
                    "recipient": "fake@gmail.com",
                    "images": [],
                    "attachments": [],
                    "text": "Some email test",
                    "html": "<div>Some message html</div>"}
        mock_logger = Mock()
        application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        application.clients.email_client.smtplib.SMTP.starttls = Mock()
        application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        test_client.email_login = Mock()
        test_client._email_server = Mock()
        test_client._email_server.quit = Mock()
        test_client._email_server.sendmail = Mock()
        test_client._logger.info = Mock()
        test_client._logger.exception = Mock()
        status = test_client.send_to_email(test_msg)
        assert test_client._logger.info.called
        assert status == 200
        assert test_client._email_server.sendmail.called
        assert test_client._email_server.sendmail.call_args[0][0] == test_client._config.EMAIL_CONFIG['sender_email']
        assert test_client._email_server.sendmail.call_args[0][1] == test_msg["recipient"]
        assert isinstance(test_client._email_server.sendmail.call_args[0][2], str)
        assert test_client._logger.exception.called is False

    def send_to_email_ok_no_attachment_provided_test(self):
        test_msg = {"subject": "subject",
                    "message": "message",
                    "recipient": "fake@gmail.com",
                    "images": [],
                    "attachments": [],
                    "text": "Some email test",
                    "html": "<div>Some message html</div>"}
        mock_logger = Mock()
        application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        application.clients.email_client.smtplib.SMTP.starttls = Mock()
        application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        test_client._email_server = Mock()
        test_client._email_server.sendmail = Mock()
        test_client._email_server.quit = Mock()
        test_client.email_login = Mock()
        test_client._logger.info = Mock()
        test_client._logger.exception = Mock()
        status = test_client.send_to_email(test_msg)
        assert status == 200
        assert test_client._email_server.sendmail.called
        assert test_client._email_server.sendmail.call_args[0][0] == test_client._config.EMAIL_CONFIG['sender_email']
        assert test_client._email_server.sendmail.call_args[0][1] == test_msg["recipient"]
        assert isinstance(test_client._email_server.sendmail.call_args[0][2], str)
        assert test_client._logger.exception.called is False

    def send_to_email_ko_test(self):
        test_msg = Mock()
        mock_logger = Mock()
        application.clients.email_client.smtplib.SMTP.ehlo = Mock()
        application.clients.email_client.smtplib.SMTP.starttls = Mock()
        application.clients.email_client.smtplib.SMTP.login = Mock()
        test_client = EmailClient(config, mock_logger)
        test_client._email_server = Mock()
        test_client._email_server.sendmail = Mock(side_effect=Exception)
        test_client._logger.info = Mock()
        test_client._logger.exception = Mock()
        status = test_client.send_to_email(test_msg)
        assert status == 500
        assert test_client._logger.info.called is False
        assert test_client._logger.exception.called
