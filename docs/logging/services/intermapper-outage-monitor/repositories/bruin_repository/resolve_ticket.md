## Resolve ticket

```python
logger.info(f"Resolving ticket {ticket_id} (affected detail ID: {detail_id})...")
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when resolving ticket {ticket_id} -> {e}"
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Ticket {ticket_id} resolved!")
```

* If response status for resolve ticket is not ok:
  ```python
  err_msg = (
      f"Error while resolving ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```