## Mark as read

* If there is not a matching password for the given email account:
  ```python
  unread_emails = f"Email account {email_account}'s password is not in our MONITORABLE_EMAIL_ACCOUNTS dict"
  logger.error(unread_emails)
  ```
  END

[EmailReaderClient::mark_as_read](../../clients/email_reader_client/mark_as_read.md)
