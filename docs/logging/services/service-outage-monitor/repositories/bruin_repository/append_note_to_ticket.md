## Append note to ticket

* If the note is meant to be appended to tasks linked to particular service numbers:
  ```python
  logger.info(
      f'Appending note for service number(s) {", ".join(service_numbers)} in ticket {ticket_id}...'
  )
  ```
* Otherwise:
  ```python
  logger.info(f"Appending note for all service number(s) in ticket {ticket_id}...")
  ```

* If there's an error while asking for the data to the `bruin-bridge`:
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
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment. Note was {note}. Error: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
  END