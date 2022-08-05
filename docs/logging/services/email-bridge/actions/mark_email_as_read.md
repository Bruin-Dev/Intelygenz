## Subject: mark.email.read.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot mark email as read using {json.dumps(msg)}. Must include body in request")
  ```
  END

* If message body doesn't have `msg_uid`, `email_account` fields:
  ```python
  self._logger.error(f"Cannot get unread emails with {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
self._logger.info(f"Attempting to mark message {msg_uid} from email account {email_account} as read")
```

[mark_as_read](../repositories/email_reader_repository/mark_as_read.md)

```python
self._logger.info(
   f"Received the following from attempting to mark message {msg_uid} as read: "
   f'{json.dumps(response["body"], indent=2)}'
)
```

