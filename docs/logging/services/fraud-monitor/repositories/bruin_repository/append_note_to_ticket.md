## Append note to ticket

* If service number:
  ```python
  logger.info(f'Appending note for service number(s) {", ".join(service_numbers)} in ticket {ticket_id}...')
  ```
* Else:
  ```python
  logger.info(f"Appending note for all service number(s) in ticket {ticket_id}...")
  ```
* If Exception:
  ```python
  logger.error(
      f"An error occurred when appending a ticket note to ticket {ticket_id}. "
      f"Ticket note: {note}. Error: {e}"
  )
  ```
* If status not ok:
  ```python
  logger.error(
      f"Error while appending note to ticket {ticket_id} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment. Note was {note}. Error: "
      f"Error {response_status} - {response_body}"
  )
  ```