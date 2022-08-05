## Create connection

Given the email server `imaplib.IMAP4_SSL("imap.gmail.com")` try to create a connection

* If there is an error while fetching the emails:
  ```python
  self._logger.error(f"There was an error trying to create the connection to the inbox: {err}")
  ```
  END
