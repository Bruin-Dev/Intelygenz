## Append tnba notes
* for ticket id in notes ticket id:
  ```
  self._logger.info(f"Appending {len(notes)} TNBA notes to ticket {ticket_id}...")
  ```
  * [append_multiple_notes_to_ticket](../repositories/bruin_repository/append_multiple_notes_to_ticket.md)
  * If append multiple notes status is not OK:
    ```
    self._logger.warning(f"Bad status calling append multiple notes to ticket id: {ticket_id}."
                                     f" Skipping ...")
    ```