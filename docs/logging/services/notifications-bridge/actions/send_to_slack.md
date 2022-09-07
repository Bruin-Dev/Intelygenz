## Subject: notification.slack.request

_Message arrives at subject_


* If message doesn't have a body:
  ```python
  logger.error(f"Cannot send to slack with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `message` filter:
  ```python
  logger.error(f'Cannot send to slack with {json.dumps(payload)}. Need parameters "message"')
  ```
  END

[send_to_slack](../repositories/slack_repository/send_to_slack.md)

```python
logger.info(
    f"Notifications send to slack published in event bus for request {json.dumps(msg)}. Message published was {notification_response}"
)
```
