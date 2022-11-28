## Subject: bruin.notification.email.milestone

_Message arrives at subject_

* If message body doesn't have `ticket_id`, `notification_type`, or `service_number` :
  ```python
  logger.error(f"Cannot send milestone email using {json.dumps(msg)}. " f"JSON malformed")
  ```
  END

```python
logger.info(
    f'Sending milestone email for ticket "{ticket_id}", service number "{service_number}"'
    f' and notification type "{notification_type}"...'
)
```

[post_notification_email_milestone](../repositories/bruin_repository/post_notification_email_milestone.md)

* If status from `post_notification_email_milestone` is in range of 200 - 300:
  ```python
  logger.info(
      f"Milestone email notification successfully sent for ticket {ticket_id}, service number"
      f" {service_number} and notification type {notification_type}"
  )
  ```
* Else
    ```python
    logger.error(
        f"Error sending milestone email notification for ticket {ticket_id}, service number"
        f" {service_number} and notification type {notification_type}: Status:"
        f' {response["status"]} body: {response["body"]}'
    )
    ```

    END
