## Unresolve task for affecting ticket Documentation

```
self._logger.info(
            f"Unresolving task related to edge {serial_number} of Service Affecting ticket {ticket_id} due to a "
            f"{trouble.value} trouble detected in interface {interface}..."
        )
```

* if not working_environment == "production"
  ```
  self._logger.info(
                f"Task related to edge {serial_number} of Service Affecting ticket {ticket_id} will not be unresolved "
                f"because of the {trouble.value} trouble detected in interface {interface}, since the current "
                f"environment is {working_environment.upper()}"
            )
  ```

* [Open ticket](../repositories/bruin_repository/open_ticket.md)

```
self._logger.info(
            f"Task related to edge {serial_number} of Service Affecting ticket {ticket_id} was successfully "
            f"unresolved! The cause was a {trouble.value} trouble detected in interface {interface}"
        )
```

* [Append note to ticket](../repositories/bruin_repository/append_note_to_ticket.md)
* if should_schedule_hnoc_forwarding
  ```
  self._logger.info(
                f"Forwarding reopened task for serial {serial_number} of ticket {ticket_id} to the HNOC queue..."
            )
  ```
  * [Schedule forward to HNOC queue](_schedule_forward_to_hnoc_queue.md)

* else
  ```
  self._logger.info(
                f"Ticket_id: {ticket_id} for serial: {serial_number} with link_label: "
                f"{link_data['link_status']['displayName']} is a blacklisted link and "
                f"should not be forwarded to HNOC. Skipping forward to HNOC..."
            )
  
  self._logger.info(
                f"Sending an email for the reopened task of ticket_id: {ticket_id} "
                f"with serial: {serial_number} instead of scheduling forward to HNOC..."
            )
  ```
  * [Send initial email milestone notification](../repositories/bruin_repository/send_initial_email_milestone_notification.md)
  * if email_response["status"] not in range(200, 300)
    ```
    self._logger.error(
                    f"Reminder email of edge {serial_number} could not be sent for ticket" f" {ticket_id}!"
                )
    ```
  * [Append reminder note](_append_reminder_note.md)
  * if append_note_response["status"] not in range(200, 300)
    ```
    self._logger.error(
                    f"Reminder note of edge {serial_number} could not be appended to ticket" f" {ticket_id}!"
                )
    ```