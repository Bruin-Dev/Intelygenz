## Reboot DiGi link from edge

```python
logger.info(f"Rebooting DiGi link from {serial_number} (ticket {ticket_id})...")
```

* If there's an error while asking for the data to the `digi-bridge`:
  ```python
  err_msg = (
      f"An error occurred when attempting a DiGi reboot for link from edge {serial_number} "
      f"(ticket {ticket_id}) -> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"DiGi link from {serial_number} (ticket {ticket_id}) rebooted!")
```

* If response status for reboot DiGi link from edge is not ok:
  ```python
  err_msg = (
      f"Error while attempting a DiGi reboot for ticket {ticket_id} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```