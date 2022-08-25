## Append note to ticket

```python
logger.info(f"Appending note to ticket {ticket_id}... Note contents: {note}")
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when appending a ticket note to ticket {ticket_id}. "
      f"Ticket note: {note}. Error: {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for append note to ticket is not ok:
  ```python
  err_msg = (
      f"Error while appending note to ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
* Otherwise:
  ```python
  logger.info(f"Note appended to ticket {ticket_id}!")
  ```