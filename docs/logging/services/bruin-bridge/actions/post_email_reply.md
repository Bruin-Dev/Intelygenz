## Subject: bruin.email.reply

_Message arrives at subject_ 

_Try to use `parse_obj` on Message body_

* `ValidationError` caught:
  ```python
  logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
  ```
  END


```python
logger.info(f"Sending email {message_body.parent_email_id} an auto-reply")
```

[post](../clients/bruin_session/post.md)

* if response.status from calling `post` is `HTTPStatus.UNAUTHORIZED`
  ```python
  logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  END
