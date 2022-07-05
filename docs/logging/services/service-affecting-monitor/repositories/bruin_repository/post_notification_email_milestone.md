## Post notification email milestone Documentation

```
self._logger.info(
                f"Sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}..."
            )
```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred when sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}...-> {e}"
            )
  ```

* if response_status in range(200, 300)
  ```
  self._logger.info(
                    f"Email sent for ticket {ticket_id}, service number {service_number} "
                    f"and notification type {notification_type}!"
                )
  ```

* else
  ```
  self._logger.error(
                    f"Error while sending email for ticket {ticket_id}, "
                    f"service_number {service_number} and notification type {notification_type} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )
  ```