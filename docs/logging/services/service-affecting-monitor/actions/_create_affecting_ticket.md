## Create affecting ticket Documentation

```
self._logger.info(
            f"Creating Service Affecting ticket to report a {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number}..."
        )
```

* if not working_environment == "production"
  ```
  self._logger.info(
                f"No Service Affecting ticket will be created to report a {trouble.value} trouble detected in "
                f"interface {interface} of edge {serial_number}, since the current environment is "
                f"{working_environment.upper()}"
            )
  ```

* [Create affecting ticket](../repositories/bruin_repository/create_affecting_ticket.md)

```
self._logger.info(
            f"Service Affecting ticket to report {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number} was successfully created! Ticket ID is {ticket_id}"
        )
```

* [Append note to ticket](../repositories/bruin_repository/append_note_to_ticket.md)

* if trouble is not AffectingTroubles.BOUNCING
    * if should_schedule_hnoc_forwarding
      * [Schedule forward to hnoc queue](_schedule_forward_to_hnoc_queue.md)
    * else
      ```
      self._logger.info(
                    f"Ticket_id: {ticket_id} for serial: {serial_number} with link_label: "
                    f"{link_data['link_status']['displayName']} is a blacklisted link and "
                    f"should not be forwarded to HNOC. Skipping forward to HNOC..."
                )

      self._logger.info(
                    f"Sending an email for ticket_id: {ticket_id} "
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