## Unresolve task for ticket
```
self._logger.info(f"Unresolving task related to {service_number} of Fraud ticket {ticket_id}...")
```
* If environment not PRODUCTION:
  ```
  self._logger.info(
                f"Task related to {service_number} of Fraud ticket {ticket_id} will not be unresolved "
                f"since the current environment is not production"
            )
  ```
* [open_ticket](../repositories/bruin_repository/open_ticket.md)
  ```
  self._logger.warning(f"Bad status calling to open ticket with ticket id: {ticket_id}. "
                                 f"Unresolve task for ticket return FALSE")
  ```
```
self._logger.info(f"Task related to {service_number} of Fraud ticket {ticket_id} was successfully unresolved!")
```
* [append_note_to_ticket](../repositories/bruin_repository/append_note_to_ticket.md)
  ```
  self._logger.warning(f"Bad status calling to append note to ticket id: {ticket_id} and service number:"
                                 f"{service_number}. Unresolve task for ticket return FALSE")
  ```
```
self._logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
```