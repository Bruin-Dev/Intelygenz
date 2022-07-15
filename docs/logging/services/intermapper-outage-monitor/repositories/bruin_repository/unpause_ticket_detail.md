## Unpause ticket detail

```python
self._logger.info(f"Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...")
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. "
      f"Error: {e}"
  )
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for unpause ticket detail is not ok:
  ```python
  err_msg = (
      f"Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment. "
      f"Error: Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(f"Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!")
  ```