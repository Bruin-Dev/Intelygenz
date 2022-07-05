## Open ticket Documentation

```
self._logger.info(f"Opening ticket {ticket_id} (affected detail ID: {detail_id})...")

self._logger.info(f"Ticket {ticket_id} opened!")
```

* if `Exception`
  ```
  self._logger.error(f"An error occurred when opening outage ticket {ticket_id} -> {e}")
  ```

* if response_status not in range(200, 300)
  ```
  self._logger.error(
                    f"Error while opening outage ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )
  ```
  