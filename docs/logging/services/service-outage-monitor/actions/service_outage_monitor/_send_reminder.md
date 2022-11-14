## Send reminder e-mail milestone notification via Bruin

```python
logger.info(f"Attempting to send reminder for service number {service_number} to ticket {ticket_id}")
```

* If the last reminder was sent too recently:
  ```python
  logger.info(
      f"No Reminder note will be appended for service number {service_number} to ticket {ticket_id},"
      f" since either the last documentation cycle started or the last reminder"
      f" was sent too recently"
  )
  ```
  END

[BruinRepository::send_reminder_email_milestone_notification](../../repositories/bruin_repository/send_reminder_email_milestone_notification.md)

* If response status for send reminder e-mail milestone notification is not ok:
  ```python
  logger.error(f"Reminder email of edge {service_number} could not be sent for ticket {ticket_id}!")
  ```
  END

[_append_reminder_note](_append_reminder_note.md)

* If response status for append Reminder note to ticket is not ok:
  ```python
  logger.error(f"Reminder note of edge {service_number} could not be appended to ticket {ticket_id}!")
  ```
  END

```python
logger.info(f"Reminder note of edge {service_number} was successfully appended to ticket {ticket_id}!")
```