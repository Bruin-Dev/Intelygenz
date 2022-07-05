## Append latest trouble to ticket Documentation

```
self._logger.info(
            f"Appending Service Affecting trouble note to ticket {ticket_id} for {trouble.value} trouble detected in "
            f"interface {interface} of edge {serial_number}..."
        )
```

* if is_there_any_note_for_trouble
  ```
  self._logger.info(
                f"No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble "
                f"detected in interface {interface} of edge {serial_number}. A note for this trouble was already "
                f"appended to the ticket after the latest re-open (or ticket creation)"
            )
  ```

* if not working_environment == "production"
  ```
  self._logger.info(
                f"No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble "
                f"detected in interface {interface} of edge {serial_number}, since the current environment is "
                f"{working_environment.upper()}"
            )
  ```

* [Append note to ticket](../repositories/bruin_repository/append_note_to_ticket.md)

```
self._logger.info(
            f"Service Affecting trouble note for {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number} was successfully appended to ticket {ticket_id}!"
        )
```
