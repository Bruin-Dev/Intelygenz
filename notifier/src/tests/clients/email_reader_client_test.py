import imaplib
from unittest.mock import Mock, patch

from application.clients import email_reader_client as email_reader_client_module
from application.clients.email_reader_client import EmailReaderClient
from config import testconfig as config


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
    'msg_uid': '1234'
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
            mail_client._create_connection()
            mock_imap.assert_called_once()
            logger.error.assert_called_once()

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
            mail_client._login(email, password)
            mock_post.assert_called_once()
            mock_select.assert_called_once()
            logger.error.assert_called_once()

    def login_KO_test(self):
        logger = Mock()
        logger.error = Mock()

        email = 'fake@email.com'
        password = '123'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'login', side_effect=imaplib.IMAP4_SSL.error):
            mail_client = EmailReaderClient(config, logger)
            mail_client._login(email, password)
            logger.error.assert_called_once()

    def logout_OK_test(self):
        logger = Mock()
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'close', return_value=True) as mock_close,\
                patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'logout', return_value=True) as mock_logout:
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._logout()
            mock_close.assert_called_once()
            mock_logout.assert_called_once()

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
            mail_client._create_connection()
            mail_client._logout()
            mock_close.assert_called_once()
            mock_logout.assert_not_called()
            logger.error.assert_called_once()

    def reset_connection_test(self):
        logger = Mock()

        mail_client = EmailReaderClient(config, logger)
        mail_client._login = Mock()
        mail_client._logout = Mock()

        email = 'fake@email.com'
        password = '123'

        mail_client._reset_connection(email, password)

        mail_client._login.assert_called_once_with(email, password)
        mail_client._logout.assert_called_once()

    def get_unread_messages_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']
        message_object = MessageObject()
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._search_messages = Mock(return_value=['1234'])
            mail_client._extract_data_from_message = Mock(return_value=['1234 2345'])
            mail_client._get_message_uid = Mock(return_value=MESSAGE_1['msg_uid'])
            mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
            mail_client._mark_as_unread = Mock(return_value=True)
            unread_messages = mail_client.get_unread_messages(email, password, email_filter)

            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once()
            mail_client._search_messages.assert_called_once_with(email, password, email_filter[0])
            mail_client._extract_data_from_message.assert_called_once_with('1234')
            mail_client._get_message_uid.assert_called_once_with('1234')
            mail_client._get_body.assert_called_once_with(message_object)
            mail_client._mark_as_unread.assert_called_once_with(MESSAGE_1['msg_uid'], email, password)

            message_1_copy = MESSAGE_1.copy()
            message_1_copy['message'] = str(MESSAGE_1['message'])
            assert unread_messages == [message_1_copy]

    def get_unread_messages_OK_no_mark_as_read_test(self):
        logger = Mock()
        logger.error = Mock()
        email = 'fake@email.com'
        password = '123'
        email_filter = ['filter@gmail.com']

        message_object = MessageObject()
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._search_messages = Mock(return_value=['1234'])
            mail_client._extract_data_from_message = Mock(return_value=['1234 2345'])
            mail_client._get_message_uid = Mock(return_value=MESSAGE_1['msg_uid'])
            mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
            mail_client._mark_as_unread = Mock(return_value=False)
            unread_messages = mail_client.get_unread_messages(email, password, email_filter)

            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once()
            mail_client._search_messages.assert_called_once_with(email, password, email_filter[0])
            mail_client._extract_data_from_message.assert_called_once_with('1234')
            mail_client._get_message_uid.assert_called_once_with('1234')
            mail_client._get_body.assert_called_once_with(message_object)
            mail_client._mark_as_unread.assert_called_once_with(MESSAGE_1['msg_uid'], email, password)
            assert unread_messages == []
            logger.error.assert_called_with(f'Unable to mark message 1234 as unread')

    def get_unread_messages_OK_no_data_in_message_test(self):
        logger = Mock()

        email = 'fake@email.com'
        password = '123'

        email_filter = ['filter@gmail.com']

        message_object = MessageObject()
        with patch.object(email_reader_client_module.email, 'message_from_bytes', return_value=message_object):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._search_messages = Mock(return_value=['1234'])
            mail_client._extract_data_from_message = Mock(return_value=None)
            mail_client._get_message_uid = Mock(return_value=MESSAGE_1['msg_uid'])
            mail_client._get_body = Mock(return_value=MESSAGE_1['body'])
            mail_client._mark_as_unread = Mock(return_value=True)
            unread_messages = mail_client.get_unread_messages(email, password, email_filter)

            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once()
            mail_client._search_messages.assert_called_once_with(email, password, email_filter[0])
            mail_client._extract_data_from_message.assert_called_once_with('1234')
            mail_client._get_message_uid.assert_not_called()
            mail_client._get_body.assert_not_called()
            mail_client._mark_as_unread.assert_not_called()
            assert unread_messages == []

    def search_messages_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        sender_email = 'filter@gmail.com'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'search', return_value=['OK', ['mail1 mail2']]):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._reset_connection = Mock()

            data = mail_client._search_messages(email, password, sender_email)
            mail_client._reset_connection.assert_not_called()
            assert data == ['mail1', 'mail2']

    def search_messages_KO_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        sender_email = 'filter@gmail.com'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'search', return_value=['KO', 'some data']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._reset_connection = Mock()

            data = mail_client._search_messages(email, password, sender_email)
            mail_client._reset_connection.assert_not_called()
            assert data == []

    def search_messages_with_exception_test(self):
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
            mail_client._reset_connection = Mock()
            mail_client._create_connection()

            data = mail_client._search_messages(email, password, sender_email)
            mail_client._reset_connection.assert_called_once_with(email, password)
            logger.error.assert_called_with(logging_message_1)
            assert data == []

    def extract_data_from_message_OK_test(self):
        logger = Mock()
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch', return_value=['OK', 'some data']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._reset_connection = Mock()

            data = mail_client._extract_data_from_message(b'1')
            mail_client._reset_connection.assert_not_called()
            assert data == 'some data'

    def extract_data_from_message_KO_test(self):
        logger = Mock()

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch', return_value=['KO', 'some data']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._reset_connection = Mock()

            data = mail_client._extract_data_from_message(b'1')
            mail_client._reset_connection.assert_not_called()
            assert data is None

    def extract_data_from_message_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        logging_message_1 = f'Error getting message 1 due to {exception_error}'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch', side_effect=response_mock):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()

            data = mail_client._extract_data_from_message(b'1')
            logger.error.assert_called_with(logging_message_1)
            assert data is None

    def get_body_ok_test(self):
        logger = Mock()
        msg = Mock()
        msg.is_multipart = Mock(return_value=False)
        msg.get_content_charset = Mock(return_value='ascii')
        msg.get_payload = Mock(return_value=MESSAGE_1['body'])

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
        msg.get_payload.decode = Mock(return_value=MESSAGE_1['body'])

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

    def get_message_uuid_ok_test(self):
        logger = Mock()
        uid = Mock()
        uid_bytes = Mock()
        uid.split = Mock(return_value=[uid_bytes, uid_bytes, uid_bytes])
        uid_bytes.decode = Mock(return_value=MESSAGE_1['msg_uid'])
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch', return_value=['OK', [uid, uid, uid]]):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            message_uid = mail_client._get_message_uid(b'1')
            assert message_uid == MESSAGE_1['msg_uid']

    def get_message_uuid_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        uid = Mock()
        uid_bytes = Mock()
        uid.split = Mock(return_value=[uid_bytes, uid_bytes, uid_bytes])
        uid_bytes.decode = Mock(return_value=MESSAGE_1['msg_uid'])

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        logging_message_1 = f'Error getting uid from message 1 due to {exception_error}'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'fetch', side_effect=response_mock):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()

            message_uid = mail_client._get_message_uid(b'1')
            logger.error.assert_called_once_with(logging_message_1)
            assert message_uid == -1

    def mark_as_unread_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['OK', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mark_as_unread = mail_client._mark_as_unread(MESSAGE_1['msg_uid'], email, password)
            assert mark_as_unread is True

    def mark_as_unread_KO_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['KO', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mark_as_unread = mail_client._mark_as_unread(MESSAGE_1['msg_uid'], email, password)
            assert mark_as_unread is False

    def mark_as_unread_with_exception_test(self):
        logger = Mock()
        logger.error = Mock()

        exception_error = 'Some error'
        response_mock = Mock()
        response_mock.side_effect = Exception(exception_error)

        logging_message_1 = f'Error marking message {MESSAGE_1["msg_uid"]} as unread due to {exception_error}'

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', side_effect=response_mock):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._reset_connection = Mock()

            mark_as_unread = mail_client._mark_as_unread(MESSAGE_1['msg_uid'], email, password)
            mail_client._reset_connection.assert_called_once_with(email, password)
            logger.error.assert_called_once_with(logging_message_1)
            assert mark_as_unread is False

    def mark_as_read_OK_test(self):
        logger = Mock()
        email = 'fake@email.com'
        password = '123'

        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['OK', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._reset_connection = Mock()

            mark_as_read = mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once()
            mail_client._reset_connection.assert_not_called()
            assert mark_as_read is True

    def mark_as_read_KO_test(self):
        logger = Mock()

        email = 'fake@email.com'
        password = '123'
        with patch.object(email_reader_client_module.imaplib.IMAP4_SSL, 'uid', return_value=['KO', 'uid']):
            mail_client = EmailReaderClient(config, logger)
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._reset_connection = Mock()

            mark_as_read = mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_called_once()
            mail_client._reset_connection.assert_not_called()
            assert mark_as_read is False

    def mark_as_read_with_exception_test(self):
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
            mail_client._create_connection()
            mail_client._login = Mock()
            mail_client._logout = Mock()
            mail_client._reset_connection = Mock()

            mark_as_read = mail_client.mark_as_read(MESSAGE_1['msg_uid'], email, password)
            mail_client._login.assert_called_once_with(email, password)
            mail_client._logout.assert_not_called()
            mail_client._reset_connection.assert_called_once_with(email, password)
            logger.error.assert_called_with(logging_message_1)
            assert mark_as_read is False
