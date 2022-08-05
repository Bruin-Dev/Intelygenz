## Get unread emails

* If there is not a password for the given email account:
  ```python
  unread_emails = f"Email account {email_account}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict"
  self._logger.error(unread_emails)
  ```
  END

[EmailReaderClient::get_unread_messages](../../clients/email_reader_client/get_unread_messages.md) to fetch all
available emails for the desired set of filters.