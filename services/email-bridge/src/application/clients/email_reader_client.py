import asyncio
import email
import email.header
import imaplib
from datetime import datetime, timedelta
from email.header import decode_header, make_header
from typing import Dict, List


class EmailReaderClient:
    def __init__(self, config, logger):
        self._config = config
        self._logger = logger

    def _create_connection(self):
        try:
            email_server = imaplib.IMAP4_SSL("imap.gmail.com")
            return email_server
        except Exception as err:
            self._logger.error(f"There was an error trying to create the connection to the inbox: {err}")
            return None

    def _login(self, email_account, email_password):
        recipient_folder = '"[Gmail]/All Mail"'
        try:
            email_server = self._create_connection()
            if email_server is None:
                self._logger.error("Cannot login due to current email server being None")
                return None
            email_server.login(email_account, email_password)
            resp, _ = email_server.select(recipient_folder)
            if resp != "OK":
                self._logger.error(f"Unable to open the {recipient_folder} folder")
                return None
            self._logger.info(f"Logged in to Gmail mailbox!")
            return email_server
        except imaplib.IMAP4_SSL.error as err:
            self._logger.error(f"There was an error trying to login into the inbox: {err}")
            return None

    def _logout(self, email_server):
        if email_server is None:
            self._logger.error(f"Cannot log out due to current email server being None")
            return
        try:
            email_server.close()
            email_server.logout()
        except Exception as err:
            self._logger.error(
                f"Cannot close connection due to {err} of type {type(err).__name__}. Proceeding to logout..."
            )

        self._logger.info(f"Logged out from Gmail!")

    async def get_unread_messages(
        self, email_account: str, email_password: str, email_filter: List[str], lookup_days: int
    ) -> List[Dict[str, str]]:
        email_server = self._login(email_account, email_password)
        if email_server is None:
            self._logger.error(
                f"Cannot obtain unread messages due to current email server being None. "
                f"Returning empty list of unread messages"
            )
            return []
        unread_messages = []
        messages = []
        for sender_email in email_filter:
            messages += await self._search_messages(sender_email, email_server, lookup_days)

        if messages:
            msgs = ",".join(m.decode("utf-8") for m in messages)
            fetch_resp_code, data = email_server.fetch(msgs, "(BODY.PEEK[] UID)")

            if fetch_resp_code == "OK":
                for msg_parts in data:
                    if msg_parts == b")":
                        continue
                    msg = email.message_from_bytes(msg_parts[1])
                    msg_uid = msg_parts[0].split()[2].decode("utf-8")
                    body = self._get_body(msg)
                    subject = str(make_header(decode_header(msg["Subject"])))

                    unread_messages.append(
                        {"message": msg.as_string(), "subject": subject, "body": body, "msg_uid": msg_uid}
                    )
            else:
                self._logger.error(f"Error while getting unread messages: FETCH response code is not OK")
        else:
            self._logger.info("No unread messages found")
        self._logout(email_server)
        return unread_messages

    async def _search_messages(
        self, sender_email: str, email_server: imaplib.IMAP4_SSL, lookup_days: int
    ) -> List[bytes]:

        try:
            lookup_date = (datetime.now() - timedelta(days=lookup_days)).strftime("%d-%b-%Y")
            search_resp_code, messages = email_server.search(
                None, "(UNSEEN)", f'(SINCE "{lookup_date}")', f'(FROM "{sender_email}")'
            )
            await asyncio.sleep(0)
            messages = messages[0].split()
            self._logger.info(f"Search resp code: {search_resp_code}. Number of unseen messages: {len(messages)}")
        except Exception as err:
            self._logger.error(f"Unable to access the unread mails due to {err}")
            return []
        if search_resp_code != "OK":
            self._logger.error(f"Unable to access the unread mails")
            return []
        self._logger.info(f"Messages to process in next batch: {messages}")
        return messages

    def _get_body(self, msg):
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    msg_type = part.get_content_type()
                    disp = str(part.get("Content-Disposition"))
                    if msg_type == "text/plain" and "attachment" not in disp:
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                        break
            else:
                charset = msg.get_content_charset()
                if charset is not None:
                    body = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                else:
                    body = msg.get_payload()
        except Exception as err:
            self._logger.error(f"Error getting body from message {msg}  due to {err}")

        return "\n".join(body.splitlines())

    async def mark_as_read(self, msg_uid, email_account, email_password):
        email_server = self._login(email_account, email_password)
        if email_server is None:
            self._logger.error(f"Cannot mark email {msg_uid} as read due to email server being None")
            return False
        try:
            response, _ = email_server.uid("STORE", msg_uid, "+FLAGS", r"(\Seen)")
            await asyncio.sleep(0)
            self._logout(email_server)
        except Exception as err:
            self._logger.error(f"Error marking message {msg_uid} as read due to {err}")
            return False

        if response != "OK":
            return False
        return True
