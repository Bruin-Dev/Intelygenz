## Re-Open ticket task

```python
logger.info(f"Opening ticket {ticket_id} (affected detail ID: {detail_id})...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when opening outage ticket {ticket_id} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Ticket {ticket_id} opened!")
```

* If response status for re-open task is not ok:
  ```python
  err_msg = (
      f"Error while opening outage ticket {ticket_id} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
  END