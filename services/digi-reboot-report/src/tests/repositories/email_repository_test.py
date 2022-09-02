from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application.repositories import email_repository as email_repository_module
from application.repositories.email_repository import EmailRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self):
        event_bus = Mock()
        config = testconfig

        email_repository = EmailRepository(event_bus, config)

        assert email_repository._event_bus is event_bus
        assert email_repository._config is config

    @pytest.mark.asyncio
    async def send_email_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        config = testconfig

        datetime_now = datetime.now()

        yesterday_date = datetime_now - timedelta(days=2)

        html = f"""\
        <html>
          <head></head>
          <body>
            <p>Please see more recent report with data through the end of {yesterday_date.strftime("%Y-%m-%d")}.
               <br>
               This report is generated by the MetTel IPA system.
            </p>
          </body>
        </html>
        """

        email_repository = EmailRepository(event_bus, config)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(email_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                await email_repository.send_email("test.csv")

        assert event_bus.rpc_request.call_args[0][0] == "notification.email.request"
        assert event_bus.rpc_request.call_args[0][1]["email_data"]["html"] == html
        assert event_bus.rpc_request.call_args[0][1]["email_data"]["attachments"][0]["name"] == "digi_reboot_report.csv"