## Reopen outage ticket
```
self._logger.info(f"Reopening outage ticket {ticket_id} for serial {serial_number}...")
```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
* If get ticket details status is not Ok:
  ```
  self._logger.info(f"Bad status calling to get ticket details. Skipping reopen ticket ...")
  ```
* [open_ticket](../../repositories/bruin_repository/open_ticket.md)
* If open ticket status is Ok:
  ```
  self._logger.info(f"Detail {detail_id_for_reopening} of outage ticket {ticket_id} reopened successfully.")
  ```
  * [_append_triage_note](_append_triage_note.md)
* Else:
  ```
  self._logger.error(f"Reopening for detail {detail_id_for_reopening} of outage ticket {ticket_id} failed.")
  ```