## Subject: notification.email.request

_Message arrives at subject_

* If message does not contain `email_data`:
  ```python
  logger.error(f'Cannot send to email with {json.dumps(payload)}. JSON malformed"')
  END
  ```
[send_to_email](../repositories/email_repository/send_to_email.md)