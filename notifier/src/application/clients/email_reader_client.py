import asyncio
import email
import email.header
import imaplib
from datetime import datetime, timedelta
from email.header import decode_header, make_header


class EmailReaderClient:

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger
        self._email_server = None

    def _create_connection(self):
        try:
            self._email_server = imaplib.IMAP4_SSL('imap.gmail.com')
        except Exception as err:
            self._logger.error(f'There was an error trying to create the connection to the inbox: {err}')

    def _login(self, email_account, email_password):
        recipient_folder = '"[Gmail]/All Mail"'
        try:
            self._create_connection()
            self._email_server.login(email_account, email_password)
            resp, _ = self._email_server.select(recipient_folder)
            if resp != 'OK':
                self._logger.error(f'Unable to open the {recipient_folder} folder')

            self._logger.info(f'Logged in to Gmail mailbox!')
        except imaplib.IMAP4_SSL.error as err:
            self._logger.error(f'There was an error trying to login into the inbox: {err}')

    def _logout(self):
        try:
            self._email_server.close()
            self._email_server.logout()
        except Exception as err:
            self._logger.error(
                f'Cannot close connection due to {err} of type {type(err).__name__}. Proceeding to logout...')

        self._logger.info(f'Logged out from Gmail!')

    def _reset_connection(self, email_account, email_password):
        self._logout()
        self._login(email_account, email_password)

    async def get_unread_messages(self, email_account, email_password, email_filter):
        self._login(email_account, email_password)
        unread_messages = []
        messages = []
        for sender_email in email_filter:
            messages += await self._search_messages(email_account, email_password, sender_email)

        for num in messages:
            data = await self._extract_data_from_message(num)
            if data is not None:
                msg = email.message_from_bytes(data[0][1])
                msg_uid = await self._get_message_uid(num)
                body = self._get_body(msg)
                subject = str(make_header(decode_header(msg['Subject'])))

                response = await self._mark_as_unread(msg_uid, email_account, email_password)
                if not response:
                    self._logger.error(f'Unable to mark message {msg_uid} as unread')
                    continue

                unread_messages.append({'message': msg.as_string(), 'subject': subject,
                                        'body': body, 'msg_uid': msg_uid})

        self._logout()
        return unread_messages

    async def _search_messages(self, email_account, email_password, sender_email):

        try:
            todays_date = (datetime.now() - timedelta(hours=24)).strftime("%d-%b-%Y")
            search_resp_code, messages = self._email_server.search(None, '(UNSEEN)', f'(SINCE "{todays_date}")',
                                                                   f'(FROM "{sender_email}")')
            await asyncio.sleep(0)
            messages = messages[0].split()
            self._logger.info(f'Search resp code: {search_resp_code}. Number of unseen messages: {len(messages)}')
        except Exception as err:
            self._logger.error(f'Unable to access the unread mails due to {err}')
            self._reset_connection(email_account, email_password)
            return []
        if search_resp_code != 'OK':
            self._logger.error(f'Unable to access the unread mails')
            return []
        self._logger.info(f'Messages to process in next batch: {messages}')
        return messages

    async def _extract_data_from_message(self, num):

        self._logger.info(f'Processing message with num {num}')
        try:
            fetch_resp_code, data = self._email_server.fetch(num, '(RFC822)')
            await asyncio.sleep(0)
        except Exception as err:
            self._logger.error(f'Error getting message {num.decode()} due to {err}')
            return None

        if fetch_resp_code != 'OK':
            self._logger.error(f'Error getting message {num.decode()}')
            return None
        return data

    def _get_body(self, msg):
        body = ''
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    msg_type = part.get_content_type()
                    disp = str(part.get('Content-Disposition'))
                    if msg_type == 'text/plain' and 'attachment' not in disp:
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                        break
            else:
                body = msg.get_payload()
        except Exception as err:
            self._logger.error(f'Error getting body from message {msg}  due to {err}')

        return body

    async def _get_message_uid(self, num):

        try:
            uid_bytes = self._email_server.fetch(num, 'UID')[1][0].split()[2]
            await asyncio.sleep(0)
        except Exception as err:
            self._logger.error(f'Error getting uid from message {num.decode()} due to {err}')
            return -1

        uid_str = uid_bytes.decode("utf-8").strip('()')
        return uid_str

    async def _mark_as_unread(self, msg_uid, email_account, email_password):

        try:
            response, _ = self._email_server.uid('STORE', msg_uid, '-FLAGS', r'(\Seen)')
            await asyncio.sleep(0)
        except Exception as err:
            self._logger.error(f'Error marking message {msg_uid} as unread due to {err}')
            self._reset_connection(email_account, email_password)
            return False

        if response != 'OK':
            return False
        return True

    async def mark_as_read(self, msg_uid, email_account, email_password):

        try:
            self._login(email_account, email_password)
            response, _ = self._email_server.uid('STORE', msg_uid, '+FLAGS', r'(\Seen)')
            await asyncio.sleep(0)
            self._logout()
        except Exception as err:
            self._logger.error(f'Error marking message {msg_uid} as read due to {err}')
            self._reset_connection(email_account, email_password)
            return False

        if response != 'OK':
            return False
        return True
