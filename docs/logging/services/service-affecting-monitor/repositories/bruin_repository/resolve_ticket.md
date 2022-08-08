## Resolve ticket Documentation

```
self._logger.info(f"Resolving detail {detail_id} of ticket {ticket_id}...")
```

* if `Exception`
  ```
  self._logger.error(f"An error occurred while resolving detail {detail_id} of ticket {ticket_id} -> {e}")
  ```

* if response_status in range(200, 300)
  ```
  self._logger.info(f"Detail {detail_id} of ticket {ticket_id} resolved successfully!")
  ```
* else
   ```
   self._logger.error(
                      f"Error while resolving detail {detail_id} of ticket {ticket_id} in "
                      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                      f"Error {response_status} - {response_body}"
                     )
  ```
