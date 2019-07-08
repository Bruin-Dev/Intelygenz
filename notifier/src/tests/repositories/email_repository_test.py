from unittest.mock import Mock
from config import testconfig as config
from application.repositories.email_repository import EmailRepository


class TestEmailRepository:

    def instantiation_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = EmailRepository(config, mock_client, mock_logger)
        assert test_repo._config == config
        assert test_repo._email_client is mock_client
        assert test_repo._logger is mock_logger

    def send_to_email_test(self):
        test_msg = Mock()
        mock_client = Mock()
        mock_client.send_to_email = Mock(return_value=200)
        mock_logger = Mock()
        test_repo = EmailRepository(config, mock_client, mock_logger)
        status = test_repo.send_to_email(test_msg)
        assert mock_client.send_to_email.called
        assert status == 200
