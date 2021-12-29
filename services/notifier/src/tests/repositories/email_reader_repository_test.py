from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock

from application.repositories.email_reader_repository import EmailReaderRepository
from config import testconfig as config


class TestEmailReaderRepository:

    def instance_test(self):
        logger = Mock()
        email_reader_client = Mock()

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        assert email_reader_repository._config == config
        assert email_reader_repository._email_reader_client == email_reader_client
        assert email_reader_repository._logger == logger

    @pytest.mark.asyncio
    async def get_unread_emails_ok_test(self):
        email = 'fake@gmail.com'
        email_filter = ['filter@gmail.com']
        message_1 = {
            'message': {
                'From': 'Alerts@ft-sys.com',
                'To': '<aaa@bbbb.com>, <ccc@dddd.com>',
                'Date': 'Fri, 20 Mar 2020 04:34:50 -0400',
                'subject': 'Idling Alert -- TT Bank - wert wert wert',
                'Content-Type': 'text/plain; charset="us-ascii"',
                'Content-Transfer-Encoding': 'quoted-printable',
                'Message-ID': '<f2a81342-ba43-52d6-8899-babc10e001e5@JJJJ.KKKK.local>',
                'Return-Path': 'Alerts@ft-sys.com',
                'X-CCSI-Disclaimer': 'added'
            },
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': '1234'
        }
        message_2 = {
            'message': None,
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': '1234'
        }

        message_3 = {
            'message': {},
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': -1
        }
        expected_unread_emails = [message_1, message_2, message_3]
        expected_unread_emails_response = {
                                    'body': expected_unread_emails,
                                    'status': 200
        }
        logger = Mock()
        email_reader_client = Mock()
        email_reader_client.get_unread_messages = CoroutineMock(return_value=expected_unread_emails)

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        unread_emails = await email_reader_repository.get_unread_emails(email, email_filter)

        email_reader_client.get_unread_messages.assert_awaited_once_with(
            email, config.MONITORABLE_EMAIL_ACCOUNTS[email], email_filter
        )
        assert unread_emails == expected_unread_emails_response

    @pytest.mark.asyncio
    async def get_unread_emails_ko_all_failed_unread_emails_test(self):
        email = 'fake@gmail.com'
        email_filter = ['filter@gmail.com']
        message_1 = {
            'message': {
                'From': 'Alerts@ft-sys.com',
                'To': '<aaa@bbbb.com>, <ccc@dddd.com>',
                'Date': 'Fri, 20 Mar 2020 04:34:50 -0400',
                'subject': 'Idling Alert -- TT Bank - wert wert wert',
                'Content-Type': 'text/plain; charset="us-ascii"',
                'Content-Transfer-Encoding': 'quoted-printable',
                'Message-ID': '<f2a81342-ba43-52d6-8899-babc10e001e5@JJJJ.KKKK.local>',
                'Return-Path': 'Alerts@ft-sys.com',
                'X-CCSI-Disclaimer': 'added'
            },
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': '1234'
        }
        message_2 = {
            'message': None,
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': '1234'
        }

        message_3 = {
            'message': {},
            'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                    It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
            'msg_uid': -1
        }
        expected_unread_emails = [message_2, message_3]
        expected_unread_emails_response = {
                                    'body': expected_unread_emails,
                                    'status': 500
        }
        logger = Mock()
        email_reader_client = Mock()
        email_reader_client.get_unread_messages = CoroutineMock(return_value=expected_unread_emails)

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        unread_emails = await email_reader_repository.get_unread_emails(email, email_filter)

        email_reader_client.get_unread_messages.assert_awaited_once_with(
            email, config.MONITORABLE_EMAIL_ACCOUNTS[email], email_filter
        )
        assert unread_emails == expected_unread_emails_response

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_emails_test(self):
        email = 'fake@gmail.com'
        email_filter = ['filter@gmail.com']

        expected_unread_emails = []
        expected_unread_emails_response = {
                                    'body': expected_unread_emails,
                                    'status': 200
        }
        logger = Mock()
        email_reader_client = Mock()
        email_reader_client.get_unread_messages = CoroutineMock(return_value=expected_unread_emails)

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        unread_emails = await email_reader_repository.get_unread_emails(email, email_filter)

        email_reader_client.get_unread_messages.assert_awaited_once_with(
            email, config.MONITORABLE_EMAIL_ACCOUNTS[email], email_filter
        )
        assert unread_emails == expected_unread_emails_response

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_password_test(self):
        email = 'fake123@gmail.com'
        email_filter = ['filter@gmail.com']

        expected_unread_emails_response = {
            'body': f"Email account {email}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict",
            'status': 400
        }
        logger = Mock()

        email_reader_client = Mock()
        email_reader_client.get_unread_messages = CoroutineMock()

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        unread_emails = await email_reader_repository.get_unread_emails(email, email_filter)

        email_reader_client.get_unread_messages.assert_not_awaited()
        assert unread_emails == expected_unread_emails_response

    @pytest.mark.asyncio
    async def mark_as_read_ok_test(self):
        email = 'fake@gmail.com'
        msg_uid = '123'

        expected_mark_as_read_response = {
                                    'body': f'Successfully marked message {msg_uid} as read',
                                    'status': 200
        }

        logger = Mock()

        email_reader_client = Mock()
        email_reader_client.mark_as_read = CoroutineMock(return_value=True)

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        mark_as_read_response = await email_reader_repository.mark_as_read(msg_uid, email)

        email_reader_client.mark_as_read.assert_awaited_once_with(
            msg_uid, email, config.MONITORABLE_EMAIL_ACCOUNTS[email]
        )
        assert mark_as_read_response == expected_mark_as_read_response

    @pytest.mark.asyncio
    async def mark_as_read_ko_failed_to_mark_test(self):
        email = 'fake@gmail.com'
        msg_uid = '123'

        expected_mark_as_read_response = {
                                    'body': f'Failed to mark message {msg_uid} as read',
                                    'status': 500
        }

        logger = Mock()

        email_reader_client = Mock()
        email_reader_client.mark_as_read = CoroutineMock(return_value=False)

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        mark_as_read_response = await email_reader_repository.mark_as_read(msg_uid, email)

        email_reader_client.mark_as_read.assert_awaited_once_with(
            msg_uid, email, config.MONITORABLE_EMAIL_ACCOUNTS[email]
        )
        assert mark_as_read_response == expected_mark_as_read_response

    @pytest.mark.asyncio
    async def mark_as_read_ko_no_password_test(self):
        email = 'fake123@gmail.com'
        msg_uid = '123'

        expected_mark_as_read_response = {
            'body': f"Email account {email}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict",
            'status': 400
        }

        logger = Mock()

        email_reader_client = Mock()
        email_reader_client.mark_as_read = CoroutineMock()

        email_reader_repository = EmailReaderRepository(config, email_reader_client, logger)

        mark_as_read_response = await email_reader_repository.mark_as_read(msg_uid, email)

        email_reader_client.mark_as_read.assert_not_awaited()
        assert mark_as_read_response == expected_mark_as_read_response
