import imaplib
from unittest.mock import Mock, patch

import pytest
from asynctest import CoroutineMock

from application.clients import email_reader_client as email_reader_client_module
from application.clients.email_reader_client import EmailReaderClient
from config import testconfig as config

MESSAGE_1_UID_BYTES = b'1234'

MESSAGE_1 = {
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
    'subject': 'Idling Alert -- TT Bank - wert wert wert',
    'body': 'tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
            It is located at LOCATION: zxcv zxcv. It is currently on job 000000.',
    'msg_uid': MESSAGE_1_UID_BYTES.decode('utf-8')
}


class MessageObject:
    def __getitem__(self, subject):
        return 'Idling Alert -- TT Bank - wert wert wert'

    def __init__(self):
        self._email = MESSAGE_1['message']

    def as_string(self):
        return str(self._email)


class TestEmailReaderClient:

    def instance_test(self):
        logger = Mock()

        mail_client = EmailReaderClient(config, logger)

        assert mail_client._logger is logger
        assert mail_client._config is config

    def connection_OK_test(self):
        logger = Mock()
        logger.error = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Accesstoken"})
        with patch.object(email_reader_client_module.imaplib, 'IMAP4_SSL') as mock_imap:
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mock_imap.assert_called_once()
            logger.error.assert_not_called()

    def connection_KO_test(self):
        logger = Mock()
        logger.error = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Accesstoken"})
        with patch.object(email_reader_client_module.imaplib, 'IMAP4_SSL', side_effect=Exception) as mock_imap:
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mock_imap.assert_called_once()
            logger.error.assert_called_once()
            assert email_server is None

    def login_OK_test(self):
        logger = Mock()
        logger.error = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Accesstoken"})
        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'login', return_value=response_mock) as \
                mock_post,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'select', return_value=['OK', 'OK']) as \
                mock_select:
            mail_client = EmailReaderClient(config, logger)
            mail_client._login(email, password)
            mock_post.assert_called_once()
            mock_select.assert_called_once()

    def login_KO_no_email_server_test(self):
        logger = Mock()
        logger.error = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Accesstoken"})
        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'login', return_value=response_mock) as \
                mock_post,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'select', return_value=['OK', 'OK']) as \
                mock_select:
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection = Mock(return_value=None)
            email_server = mail_client._login(email, password)
            mock_post.assert_not_called()
            mock_select.assert_not_called()

            assert email_server is None

    def login_KO_folder_test(self):
        logger = Mock()
        logger.error = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Accesstoken"})

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'login', return_value=response_mock) as \
                mock_post,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'select', return_value=['KO', 'KO']) as \
                mock_select:
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._login(email, password)
            mock_post.assert_called_once()
            mock_select.assert_called_once()
            logger.error.assert_called_once()
            assert email_server is None

    def login_KO_test(self):
        logger = Mock()
        logger.error = Mock()

        email = 'fake@email.com'
        password = '123'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'login', side_effect=imaplib.IMAP4_SSL.error):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._login(email, password)
            logger.error.assert_called_once()
            assert email_server is None

    def logout_OK_test(self):
        logger = Mock()
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'close', return_value=True) as mock_close,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'logout', return_value=True) as mock_logout:
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mail_client._logout(email_server)
            mock_close.assert_called_once()
            mock_logout.assert_called_once()

    def logout_KO_no_email_server_test(self):
        logger = Mock()
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'close', return_value=True) as mock_close, \
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'logout', return_value=True) as mock_logout:
            mail_client = EmailReaderClient(config, logger)
            mail_client._logout(None)
            mock_close.assert_not_called()
            mock_logout.assert_not_called()

    def logout_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'close', side_effect=response_mock) as \
                mock_close,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'logout', return_value=True) as mock_logout:
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mail_client._logout(email_server)
            mock_close.assert_called_once()
            mock_logout.assert_not_called()
            logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def get_unread_messages_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']
        message_object = MessageObject()

        msg_bytes = Mock()
        msg_part = [msg_bytes, b'some_data']
        msg_bytes.split = Mock(return_value=[111, 999, MESSAGE_1_UID_BYTES])

        initial_fetch_return = [msg_part, b')']
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch',
                              return_value=['OK', initial_fetch_return]):
                mail_client = EmailReaderClient(config, logger)
                email_server = mail_client._create_connection()
                mail_client._login = Mock(return_value=email_server)
                mail_client._logout = Mock()
                mail_client._search_messages = CoroutineMock(return_value=[b'1234'])
                mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
                unread_messages = await mail_client.get_unread_messages(email, password, email_filter)

                mail_client._login.assert_called_once_with(email, password)
                mail_client._logout.assert_called_once_with(email_server)
                mail_client._search_messages.assert_awaited_once_with(email_filter[0], email_server)
                mail_client._get_body.assert_called_once_with(message_object)

                message_1_copy = MESSAGE_1.copy()
                message_1_copy['message'] = str(MESSAGE_1['message'])
                assert unread_messages == [message_1_copy]

    @pytest.mark.asyncio
    async def get_unread_messages_KO_no_messages_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']
        message_object = MessageObject()

        msg_bytes = Mock()
        msg_part = [msg_bytes, b'some_data']
        msg_bytes.split = Mock(return_value=[111, 999, MESSAGE_1['msg_uid']])

        initial_fetch_return = [msg_part, b')']
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch',
                              return_value=['OK', initial_fetch_return]):
                mail_client = EmailReaderClient(config, logger)
                email_server = mail_client._create_connection()
                mail_client._login = Mock(return_value=email_server)
                mail_client._logout = Mock()
                mail_client._search_messages = CoroutineMock(return_value=[])
                mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
                unread_messages = await mail_client.get_unread_messages(email, password, email_filter)

                mail_client._login.assert_called_once_with(email, password)
                mail_client._logout.assert_called_once_with(email_server)
                mail_client._search_messages.assert_awaited_once_with(email_filter[0], email_server)
                mail_client._get_body.assert_not_called()

                assert unread_messages == []

    @pytest.mark.asyncio
    async def get_unread_messages_KO_bad_fetch_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']
        message_object = MessageObject()

        msg_bytes = Mock()
        msg_part = [msg_bytes, b'some_data']
        msg_bytes.split = Mock(return_value=[111, 999, MESSAGE_1['msg_uid']])

        initial_fetch_return = [msg_part, b')']
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch',
                              return_value=['KO', initial_fetch_return]):
                mail_client = EmailReaderClient(config, logger)
                email_server = mail_client._create_connection()
                mail_client._login = Mock(return_value=email_server)
                mail_client._logout = Mock()
                mail_client._search_messages = CoroutineMock(return_value=[b'1234'])
                mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
                unread_messages = await mail_client.get_unread_messages(email, password, email_filter)

                mail_client._login.assert_called_once_with(email, password)
                mail_client._logout.assert_called_once_with(email_server)
                mail_client._search_messages.assert_awaited_once_with(email_filter[0], email_server)
                mail_client._get_body.assert_not_called()

                assert unread_messages == []

    @pytest.mark.asyncio
    async def get_unread_messages_KO_no_email_server_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']
        message_object = MessageObject()

        msg_bytes = Mock()
        msg_part = [msg_bytes, b'some_data']
        msg_bytes.split = Mock(return_value=[111, 999, MESSAGE_1['msg_uid']])

        initial_fetch_return = [msg_part, b')']
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch',
                              return_value=['KO', initial_fetch_return]):
                mail_client = EmailReaderClient(config, logger)
                mail_client._login = Mock(return_value=None)
                mail_client._logout = Mock()
                mail_client._search_messages = CoroutineMock(return_value=[b'1234'])
                mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
                unread_messages = await mail_client.get_unread_messages(email, password, email_filter)

                mail_client._login.assert_called_once_with(email, password)
                mail_client._logout.assert_not_called()
                mail_client._search_messages.assert_not_awaited()
                mail_client._get_body.assert_not_called()

                assert unread_messages == []

    @pytest.mark.asyncio
    async def search_messages_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        sender_email = 'filter@gmail.com'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'search', return_value=['OK', ['mail1 mail2']]):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()

            data = await mail_client._search_messages(sender_email, email_server)
            assert data == ['mail1', 'mail2']

    @pytest.mark.asyncio
    async def search_messages_KO_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        sender_email = 'filter@gmail.com'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'search', return_value=['KO', 'some data']):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()

            data = await mail_client._search_messages(sender_email, email_server)
            assert data == []

    @pytest.mark.asyncio
    async def search_messages_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        logging_message_1 = f'Unable to access the unread mails due to {exception_error}'

        email = 'fake@email.com'
        password = '123'

        sender_email = 'filter@gmail.com'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'search', side_effect=response_mock):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()

            data = await mail_client._search_messages(sender_email, email_server)
            logger.error.assert_called_with(logging_message_1)
            assert data == []

    def get_body_ok_test(self):
        logger = Mock()
        msg = Mock()
        msg.is_multipart = Mock(return_value=False)
        msg.get_content_charset = Mock(return_value='ascii')
        msg.get_payload = Mock()
        msg.get_payload().decode = Mock(return_value=MESSAGE_1['body'])

        mail_client = EmailReaderClient(config, logger)
        unread_messages = mail_client._get_body(msg)
        assert unread_messages == MESSAGE_1['body']

    def get_body_ok_multipart_test(self):
        logger = Mock()
        msg = Mock()
        msg.is_multipart = Mock(return_value=True)
        part_mock = Mock()
        part_mock.get_content_type = Mock(return_value='content_type')
        part_mock.get = Mock(return_value='part_get')
        msg.walk = Mock(return_value=[part_mock])
        msg.get_content_charset = Mock(return_value='ascii')
        msg.get_payload = Mock()
        msg.get_payload().decode = Mock(return_value=MESSAGE_1['body'])

        mail_client = EmailReaderClient(config, logger)
        unread_messages = mail_client._get_body(msg)
        assert unread_messages == ''

    def get_body_ok_multipart_text_plain_ok_test(self):
        logger = Mock()
        msg = Mock()
        msg.is_multipart = Mock(return_value=True)
        part_mock = Mock()
        part_mock.get_content_type = Mock(return_value='text/plain')
        part_mock.get = Mock(return_value='part_get')
        msg.walk = Mock(return_value=[part_mock])
        msg.get_content_charset = Mock(return_value='ascii')
        payload = Mock()
        part_mock.get_payload = Mock(return_value=payload)
        payload.decode = Mock(return_value=MESSAGE_1['body'])

        mail_client = EmailReaderClient(config, logger)
        unread_messages = mail_client._get_body(msg)
        assert unread_messages == MESSAGE_1['body']

    def get_body_ko_general_exception_test(self):
        logger = Mock()
        logger.error = Mock()
        msg = Mock()
        msg.is_multipart = Mock(return_value=False)
        msg.get_content_charset = Mock(return_value='ascii')
        msg.get_payload = Mock(side_effect=Exception)

        mail_client = EmailReaderClient(config, logger)
        unread_messages = mail_client._get_body(msg)
        logger.error.assert_called_once()
        assert unread_messages == ''

    @pytest.mark.asyncio
    async def mark_as_read_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['OK', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mail_client._login = Mock(return_value=email_server)
            mail_client._logout = Mock()

            mark_as_read = await mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once_with(email_server)
            assert mark_as_read is True

    @pytest.mark.asyncio
    async def mark_as_read_KO_no_email_server_test(self):
        logger = Mock()

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['KO', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._login = Mock(return_value=None)
            mail_client._logout = Mock()

            mark_as_read = await mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_not_called()
            assert mark_as_read is False

    @pytest.mark.asyncio
    async def mark_as_read_KO_test(self):
        logger = Mock()

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['KO', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mail_client._login = Mock(return_value=email_server)
            mail_client._logout = Mock()

            mark_as_read = await mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once_with(email_server)
            assert mark_as_read is False

    @pytest.mark.asyncio
    async def mark_as_read_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        logging_message_1 = f'Error marking message {MESSAGE_1["msg_uid"]} as read due to {exception_error}'

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', side_effect=response_mock):
            mail_client = EmailReaderClient(config, logger)
            email_server = mail_client._create_connection()
            mail_client._login = Mock(return_value=email_server)
            mail_client._logout = Mock()

            mark_as_read = await mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_not_called()
            logger.error.assert_called_with(logging_message_1)
            assert mark_as_read is False
