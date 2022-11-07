## Append triage note to ticket

* If the note is not larger than 1500 characters:
  ```python
  logger.info(
      f"Note for ticket {ticket_id} and {service_number} is {len(note)} characters large. "
      f"There's no need to split it."
  )
  ```
  [append_note_to_ticket](append_note_to_ticket.md)
* Otherwise:
  ```python
  logger.warning(
      f"Note for ticket {ticket_id} and {service_number} is {len(note)} characters large. "
      f"Splitting it to {total_notes} notes..."
  )
  ```

    * For each chunk:
      ```python
      logger.info(
          f"Appending Triage note ({index}/{total_notes}) to task linked to device {service_number} in "
          f"ticket {ticket_id}..."
      )
      ```
      [append_note_to_ticket](append_note_to_ticket.md)

        * If response status for append triage note to ticket is not ok:
          ```python
          logger.error(
              f"Error while appending Triage note ({index}/{total_notes}) to task linked to device "
              f"{service_number} in ticket {ticket_id}. Remaining notes won't be appended"
          )
          ```
          END

        ```python
        logger.info(
            f"Triage note ({index}/{total_notes}) appended to task linked to device "
            f"{service_number} in ticket {ticket_id}!"
        )
        ```