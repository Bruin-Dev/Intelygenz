## Append triage note if needed
```
self._logger.info(f"Checking ticket {ticket_id} to see if device {serial_number} has a triage note already...")
```
* [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
* If status is nor Ok:
  ```
  self._logger.warning(f"Bad status calling to get ticket details. Skipping append triage note ...")
  ```
* If triage note:
  ```
  self._logger.info(
                f"Triage note already exists in ticket {ticket_id} for serial {serial_number}, so no triage "
                f"note will be appended."
            )
  ```
```
self._logger.info(
            f"No triage note was found for serial {serial_number} in ticket {ticket_id}. Appending triage note..."
        )
```
* [append_triage_note_to_ticket](../repositories/bruin_repository/append_triage_note.md)
```
self._logger.info(f"Triage note for device {serial_number} appended to ticket {ticket_id}!")
```