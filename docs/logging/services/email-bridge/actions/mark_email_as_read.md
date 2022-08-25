## Subject: mark.email.read.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot mark email as read using {json.dumps(payload)}. Must include body in request")
  ```
  END

* If message body doesn't have `msg_uid`, `email_account` fields:
  ```python
  logger.error(f"Cannot mark email as read using {json.dumps(payload)}. JSON malformed")
  ```
  END

```python
logger.info(f"Attempting to mark message {msg_uid} from email account {email_account} as read")
```

[mark_as_read](../repositories/email_reader_repository/mark_as_read.md)

```python
logger.info(
   f"Received the following from attempting to mark message {msg_uid} as read: "
   f'{json.dumps(response["body"], indent=2)}'
)
```

