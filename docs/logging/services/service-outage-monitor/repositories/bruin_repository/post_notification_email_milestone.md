## Send e-mail milestone notification via Bruin

```python
logger.info(
    f"Sending email for ticket id {ticket_id}, "
    f"service_number {service_number} "
    f"and notification type {notification_type}..."
)
```

* If there's an error while asking for the data to the `bruin-bridge`:
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

* If response status for send e-mail milestone notification is not ok:
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
* Otherwise:
  ```python
  logger.info(
      f"Email sent for ticket {ticket_id}, service number {service_number} "
      f"and notification type {notification_type}!"
  )
  ```