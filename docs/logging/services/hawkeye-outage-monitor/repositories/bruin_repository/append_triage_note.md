## Append triage note
* If environment is DEV:
  ```
  self._logger.info(f"Triage note would have been appended to detail {ticket_detail_id} of ticket {ticket_id}"
                    f"(serial: {service_number}). Note: {ticket_note}. Details at app.bruin.com/t/{ticket_id}")
  ```
* Elif environment is PRODUCTION:
  * If len of ticket note is lower than 1500:
    * [append_note_to_ticket](append_note_to_ticket.md)
  * Else:
    * Split lines and send in blocks:
      * [append_note_to_ticket](append_note_to_ticket.md)