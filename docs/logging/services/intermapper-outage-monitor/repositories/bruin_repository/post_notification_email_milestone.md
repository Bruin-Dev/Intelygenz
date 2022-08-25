## Post notification email milestone

```python
logger.info(
    f"Sending email for ticket id {ticket_id}, "
    f"service_number {service_number} "
    f"and notification type {notification_type}..."
)
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when sending email for ticket id {ticket_id}, "
      f"service_number {service_number} "
      f"and notification type {notification_type}...-> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for post notification email milestone is ok:
  ```python
  logger.info(
      f"Email sent for ticket {ticket_id}, service number {service_number} "
      f"and notification type {notification_type}!"
  )
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while sending email for ticket id {ticket_id}, service_number {service_number} "
      f"and notification type {notification_type} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```