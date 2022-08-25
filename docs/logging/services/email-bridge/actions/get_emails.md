## Subject: get.email.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get unread emails with {json.dumps(payload)}. Must include body in request")
  ```
  END

* If message body doesn't have `email_account`, `email_filter`, `lookup_days` fields:
  ```python
  logger.error(f"Cannot get unread emails with {json.dumps(payload)}. JSON malformed")
  ```
  END

```python
logger.info(
f"Attempting to get all unread messages from email account {email_account} from the past {lookup_days} "
f"days coming from {email_filter}"
)
```

[get_unread_emails](../repositories/email_reader_repository/get_unread_emails.md)

```python
logger.info(f"Received the following from the gmail account {email_account}: {response['body']}")
```
