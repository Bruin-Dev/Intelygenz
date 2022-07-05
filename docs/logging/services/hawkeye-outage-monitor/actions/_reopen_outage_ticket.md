## Reopen outage ticket
```
self._logger.info(f"Reopening Hawkeye outage ticket {ticket_id}...")
```
* [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
* If status is not ok:
  ```
  self._logger.warning(f"Bad status calling get ticket details. Skipping reopen outage ticket ...") 
  ```
* [open_ticket](../repositories/bruin_repository/open_ticket.md)
* If status is not Ok:
  ```
  self._logger.error(f"[outage-ticket-creation] Outage ticket {ticket_id} reopening failed.")
  ```
* Else:
  ```
  self._logger.info(f"Hawkeye outage ticket {ticket_id} reopening succeeded.")
  ```
  * [append_note_to_ticket](../repositories/bruin_repository/append_note_to_ticket.md)