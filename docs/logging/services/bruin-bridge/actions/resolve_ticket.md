## Subject: bruin.ticket.status.resolve

_Message arrives at subject_

* If message body has `ticket_id` and `detail_id`:
  ```python
  self._logger.info(f"Updating the ticket status for ticket id: {ticket_id} to RESOLVED")
  ```
  [resolve_ticket](../repositories/bruin_repository/resolve_ticket.md)
* Else
  ```python
  self._logger.error(f"Cannot resolve a ticket using {json.dumps(msg)}. JSON malformed")
  ```
  END
