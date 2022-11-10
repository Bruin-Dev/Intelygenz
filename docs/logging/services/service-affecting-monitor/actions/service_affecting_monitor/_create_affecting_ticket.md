## Create Service Affecting ticket

```python
logger.info(
    f"Creating Service Affecting ticket to report a {trouble.value} trouble detected in interface {interface} "
    f"of edge {serial_number}..."
)
```

[BruinRepository::create_affecting_ticket](../../repositories/bruin_repository/create_affecting_ticket.md)

* If response status for create Service Affecting ticket is not ok:
  ```python
  logger.error(
      f"Error while creating Service Affecting ticket for edge {serial_number}: "
      f"{create_affecting_ticket_response}. Skipping ticket creation..."
  )
  ```
  END

```python
logger.info(
    f"Service Affecting ticket to report {trouble.value} trouble detected in interface {interface} "
    f"of edge {serial_number} was successfully created! Ticket ID is {ticket_id}"
)
```

[BruinRepository::append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)

* If the trouble that was just documented is not a Circuit Instability trouble:
    * If ticket task should be forwarded to HNOC:

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

        END

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} with link_label: "
            f"{link_data['link_status']['displayName']} is a blacklisted link and "
            f"should not be forwarded to HNOC. Skipping forward to HNOC..."
        )
        ```

        ```python
        logger.info(
            f"Sending an email for ticket_id: {ticket_id} "
            f"with serial: {serial_number} instead of scheduling forward to HNOC..."
        )
        ```

        [BruinRepository::send_initial_email_milestone_notification](../../repositories/bruin_repository/send_initial_email_milestone_notification.md)

        * If response status for send initial milestone notification is not ok:
          ```python
          logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!")
          ```
          END

        [_append_reminder_note](_append_reminder_note.md)

        * If response status for append reminder note is not ok:
          ```python
          logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket {ticket_id}!")
          ```
          END