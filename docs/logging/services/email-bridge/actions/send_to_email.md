## Subject: notification.email.request

_Message arrives at subject_

* If message body does not contain `email_data`:
  ```python
  self.logger.error(...)
  END
  ```
[send_to_email](../repositories/email_repository/send_to_email.md)