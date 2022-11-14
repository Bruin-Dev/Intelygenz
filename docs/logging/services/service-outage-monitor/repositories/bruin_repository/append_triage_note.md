## Append Triage note to ticket

* If the note is not larger than 1500 characters:
    ```python
    logger.info(
        f"Note for ticket {ticket_id} and edge {service_number} is {len(ticket_note)} characters large. "
        f"There's no need to split it."
    )
    ```

    [append_note_to_ticket](append_note_to_ticket.md)

    * If response status for append note to ticket is 503:
      ```python
      logger.error(
          f"Request to append Triage note to ticket {ticket_id} for edge {service_number} timed out"
      )
      ```
      END

    * If response status for append note to ticket is not ok:
      ```python
      logger.error(
          f"Error while appending Triage note to ticket {ticket_id} for edge {service_number}: "
          f"{append_note_response}"
      )
      ```

* Otherwise:
  ```python
  logger.warning(
      f"Note for ticket {ticket_id} and edge {service_number} is {len(ticket_note)} characters large. "
      f"Splitting it to {total_notes} notes..."
  )
  ```

    * For each chunk:
        ```python
        logger.info(
            f"Appending Triage note ({counter}/{total_notes}) to ticket {ticket_id} for "
            f"edge {service_number}..."
        )
        ```

        [append_note_to_ticket](append_note_to_ticket.md)

        * If response status for append note to ticket is 503:
          ```python
          logger.error(
              f"Request to append Triage note to ticket {ticket_id} for edge {service_number} timed out"
          )
          ```
          END

        * If response status for append note to ticket is not ok:
          ```python
          logger.error(
              f"Error while appending Triage note to ticket {ticket_id} for edge {service_number}: "
              f"{append_note_response}"
          )
          ```
          END

        ```python
        logger.info(
            f"Triage note ({counter}/{total_notes}) appended to ticket {ticket_id} for edge "
            f"{service_number}!"
        )
        ```