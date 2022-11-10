## Re-open task for Service Affecting ticket

```python
logger.info(
    f"Unresolving task related to edge {serial_number} of Service Affecting ticket {ticket_id} due to a "
    f"{trouble.value} trouble detected in interface {interface}..."
)
```

[BruinRepository::open_ticket](../../repositories/bruin_repository/open_ticket.md)

* If response status for ticket task unresolve is not ok:
  ```python
  logger.error(
      f"Error while unresolving Service Affecting ticket task for edge {serial_number}: "
      f"{unresolve_task_response}"
  )
  ```
  END

```python
logger.info(
    f"Task related to edge {serial_number} of Service Affecting ticket {ticket_id} was successfully "
    f"unresolved! The cause was a {trouble.value} trouble detected in interface {interface}"
)
```

[append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)

* If the ticket task should be forwarded to the HNOC queue:
    ```python
    logger.info(
        f"Forwarding reopened task for serial {serial_number} of ticket {ticket_id} to the HNOC queue..."
    )
    ```

    [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

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
        f"Sending an email for the reopened task of ticket_id: {ticket_id} "
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