## Append note to ticket Documentation

```
self._logger.info(f"Appending note to ticket {ticket_id}... Note contents: {note}")

self._logger.info(f"Note appended to ticket {ticket_id}!")
```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred when appending a ticket note to ticket {ticket_id}. "
                f"Ticket note: {note}. Error: {e}"
            )
  ```

* if response_status not in range(200, 300)
  ```
  self._logger.error(
                    f"Error while appending note to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
                    f"Error {response_status} - {response_body}"
                )
  ```