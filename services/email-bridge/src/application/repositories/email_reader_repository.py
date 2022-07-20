from typing import Any, Dict, List


class EmailReaderRepository:
    def __init__(self, config, email_reader_client, logger):
        self._config = config
        self._email_reader_client = email_reader_client
        self._logger = logger

    async def get_unread_emails(self, email_account: str, email_filter: List[str], lookup_days: int) -> Dict[str, Any]:
        status = 500
        if email_account in self._config.MONITORABLE_EMAIL_ACCOUNTS.keys():
            email_password = self._config.MONITORABLE_EMAIL_ACCOUNTS[email_account]
            unread_emails = await self._email_reader_client.get_unread_messages(
                email_account,
                email_password,
                email_filter,
                lookup_days,
            )

            if len(unread_emails) == 0:
                status = 200
            for email in unread_emails:
                if email["message"] is not None and email["msg_uid"] != -1:
                    status = 200
                    break
        else:
            unread_emails = f"Email account {email_account}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict"
            self._logger.error(unread_emails)
            status = 400
        return {"body": unread_emails, "status": status}

    async def mark_as_read(self, msg_uid, email_account):
        status = 500
        body = f"Failed to mark message {msg_uid} as read"
        if email_account in self._config.MONITORABLE_EMAIL_ACCOUNTS.keys():
            email_password = self._config.MONITORABLE_EMAIL_ACCOUNTS[email_account]
            marked_as_read = await self._email_reader_client.mark_as_read(msg_uid, email_account, email_password)
            if marked_as_read is True:
                body = f"Successfully marked message {msg_uid} as read"
                status = 200
        else:
            body = f"Email account {email_account}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict"
            self._logger.error(body)
            status = 400
        return {"body": body, "status": status}
