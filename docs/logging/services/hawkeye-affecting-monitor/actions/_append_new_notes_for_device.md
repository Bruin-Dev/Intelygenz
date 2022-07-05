## Append new notes for device
* If serial not in ticket:
  ```
  self._logger.info(
                f"Serial {serial_number} could not be added to the tickets mapping at the beginning of the "
                f"process, so no notes can be posted to any ticket. Skipping..."
            )
  ```
* If not notes to append:
  ```
  self._logger.info(f"No notes to append for serial {serial_number} were found. Skipping...")
  ```
* If environment is PRODUCTION:
  ```
  self._logger.info(
                f"{len(notes_to_append)} affecting notes to append to ticket {ticket_id} were found, but the current "
                "environment is not PRODUCTION. Skipping..."
            )
  ```
```
self._logger.info(
            f"Posting {len(notes_to_append)} affecting notes to ticket {ticket_id} (serial: {serial_number})..."
        )
```