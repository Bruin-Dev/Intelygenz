from unittest.mock import Mock
from config import testconfig as config
from application.repositories.telestax_repository import TeleStaxRepository


class TestTeleStaxRepository:

    def instantiation_test(self):
        mock_client = Mock()
        mock_logger = Mock()

        test_repo = TeleStaxRepository(config, mock_client, mock_logger)

        assert test_repo._config is config
        assert test_repo._telestax_client is mock_client
        assert test_repo._logger is mock_logger

    def send_to_sms_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_msg = 'This is a dummy SMS'
        sms_to = '17777777777'

        test_repo = TeleStaxRepository(config, mock_client, mock_logger)
        test_repo._telestax_client.send_to_sms = Mock()

        test_repo.send_to_sms(test_msg, sms_to)

        test_repo._telestax_client.send_to_sms.assert_called_once_with(
            test_msg,
            sms_to
        )
