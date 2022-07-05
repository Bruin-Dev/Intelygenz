## Append note to ticket
```
self._logger.info(f"Appending Fraud note to ticket {ticket_id}")
```
* If note existe:
  ```
  self._logger.info(
                f"No Fraud trouble note will be appended to ticket {ticket_id}. "
                f"A note for this email was already appended to the ticket after the latest re-open or ticket creation."
            )
  ```
* If not PRODUCTION:
  ```
  self._logger.info(
                f"No Fraud note will be appended to ticket {ticket_id} since the current environment is not production"
            )
  ```
* [append_note_to_ticket](../repositories/bruin_repository/append_note_to_ticket.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to append note to ticket id: {ticket_id}. "
                                 f"Skipping append note ...")
  ```
```
self._logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
```