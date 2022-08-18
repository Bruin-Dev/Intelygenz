from unittest.mock import Mock


class TestEmailRepository:
    def instantiation_test(self, email_repository, email_client):
        assert email_repository._email_client is email_client

    def send_to_email_test(self, email_repository):
        email_repository._email_client.send_to_email = Mock(return_value=200)
        test_msg = "This is a dummy message"

        status = email_repository.send_to_email(test_msg)

        email_repository._email_client.send_to_email.assert_called_once_with(test_msg)
        assert status == {"body": "Successfully sent email with message This is a dummy message", "status": 200}
