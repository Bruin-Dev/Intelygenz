## Send to email

  [email_login](email_login.md)
  
Call email server endpoint to send email with the set of desired query parameters.

* If there's an error while connecting to email server:
  ```python
  self._logger.exception("Error: Email not sent")
  ```
  END

* If the status of the HTTP response is `200`:
  ```python
  self._logger.info("Success: Email sent!")
  ```

Close the email server connection