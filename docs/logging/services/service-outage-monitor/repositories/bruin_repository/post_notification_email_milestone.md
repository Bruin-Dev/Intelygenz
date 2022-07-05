## post notification email milestone
```
self._logger.info(f"Sending email for ticket id {ticket_id}, service_number {service_number} and notification 
type {notification_type}...")
 ```
* If Exception:
  ```
  self._logger.info(f"An error occurred when sending email for ticket id {ticket_id}, service_number 
  {service_number} and notification type {notification_type}...-> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Email sent for ticket {ticket_id}, service number {service_number} and notification 
  type {notification_type}!")
  ```
* Else:
  ```
  self._logger.info(f"Error while sending email for ticket {ticket_id}, service_number {service_number} and 
  notification type {notification_type} in "
  f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
  f"Error {response_status} - {response_body}")
  ```