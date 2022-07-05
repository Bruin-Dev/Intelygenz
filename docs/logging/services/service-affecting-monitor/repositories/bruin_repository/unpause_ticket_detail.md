## Unpause ticket detail Documentation

```
self._logger.info(f"Unpausing detail of ticket {ticket_id} related to serial number {service_number}...")
```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred when unpausing detail of ticket {ticket_id} related to serial number "
                f"{service_number}. Error: {e}"
            )
  ```
  
* if response_status in range(200, 300)
  ```
  self._logger.info(
                    f"Detail of ticket {ticket_id} related to serial number {service_number}) was unpaused!"
                )
  ```
* else
  ```
  self._logger.error(
                    f"Error while unpausing detail of ticket {ticket_id} related to serial number {service_number}) in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}"
                )
  ```
  