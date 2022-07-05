## Attempt ticket creation

```
self._logger.info(f"[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...")
```

* [create_outage_ticket](../../repositories/bruin_repository/create_outage_ticket.md)

```
self._logger.info(f"[{outage_type.value}] Bruin response for ticket creation for edge {edge}: "
                f"{ticket_creation_response}")
```

* If status is OK:
  ```
  self._logger.info(f"[{outage_type.value}] Successfully created outage ticket for edge {edge}.")
  ```
  * [_append_triage_note](_append_triage_note.md)
  * [_change_severity](_change_ticket_severity.md)
  * If should schedule forward to hnoc queue:
    * [schedule_forward_to_hnoc_queue](schedule_forward_to_hnoc_queue.md)
  * Else:
    ```
    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                          f"with link_data: {edge_links} has a blacklisted link and "
                          f"should not be forwarded to HNOC. Skipping forward to HNOC...")
    self._logger.info(
                          f"Sending an email for ticket_id: {ticket_id} "
                          f"with serial: {serial_number} instead of scheduling forward to HNOC..."
                      )
    ```
    * [send_initial_email_milestone_notification](../../repositories/bruin_repository/send_initial_email_milestone_notification.md)
    * If send email milestone status not ok:
      ```
      self._logger.error(
                              f"Reminder email of edge {serial_number} could not be sent for ticket" f" {ticket_id}!"
                          )
      ```
    * Else:
      * [_append_reminder_note](_append_reminder_note.md)
      * If append reminder note status is not ok:
        ```
        self._logger.error(
                                  f"Reminder note of edge {serial_number} could not be appended to ticket"
                                  f" {ticket_id}!"
                              )
        ```
      * [_check_for_digi_reboot](_check_for_digi_reboot.md)
* If status 409:
  ```
  self._logger.info(f"[{outage_type.value}] Faulty edge {serial_number} already has an outage ticket in "
                    f"progress (ID = {ticket_id}). Skipping outage ticket creation for "
                     "this edge...")
  ```
  * [_change_ticket_severity](_change_ticket_severity.md)
  * If change severity is different to NOT_CHANGED:
    * If should schedule hnoc forwarding:
      * [schedule_forward_to_hnoc_queue](schedule_forward_to_hnoc_queue.md)
    * Else:
      ```
      self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
                        f"should not be forwarded to HNOC. Skipping forward to HNOC...")
      ```
      * [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
      * [_send_reminder](_send_reminder.md)
      ************************************************************************************** MIRAR ESTO
  * [_check_for_failed_digi_reboot](_check_for_failed_digi_reboot.md)
  * [_attempt_forward_to_asr](_attempt_forward_to_asr.md)
* If status 471:
  ```
  self._logger.info(f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
                    f"(ID = {ticket_id}). Re-opening ticket...")
  ```
  * [_reopen_outage_ticket](_reopen_outage_ticket.md)
  * [_change_ticket_severity](_change_ticket_severity.md)
  * If should schedule hnoc forwarding:
    * [schedule_forward_to_hnoc_queue](schedule_forward_to_hnoc_queue.md)
  * Else:
    ```
    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
                        f"should not be forwarded to HNOC. Skipping forward to HNOC...")
    self._logger.info(
                        f"Sending an email for ticket_id: {ticket_id} "
                        f"with serial: {serial_number} instead of scheduling forward to HNOC..."
                    )
    ```
    * [send_initial_email_milestone_notification](../../repositories/bruin_repository/send_initial_email_milestone_notification.md)
    * If send email is not Ok:
      ```
      self._logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket" f" {ticket_id}!")
      ```
    * Else:
      * [_append_reminder_note](_append_reminder_note.md)
      * If append reminder is not Ok:
        ```
        self._logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!")
        ```
* If status 492
  ```
  self._logger.info(f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
                    f"(ID = {ticket_id}). Its ticket detail was automatically unresolved "
                    f"by Bruin. Appending reopen note to ticket...")
  ```
  * [_append_triage_note](_append_triage_note.md)
  * [_change_ticket_severity](_change_ticket_severity.md)
  * If should schedule hnoc forwarding:
    * [schedule_forward_to_hnoc_queue](schedule_forward_to_hnoc_queue.md)
  * Else:
    ```
    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
                        f"should not be forwarded to HNOC. Skipping forward to HNOC...")
    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                        f"with serial: {serial_number} instead of scheduling forward to HNOC...")
    ```
    * [send_initial_email_milestone_notification](../../repositories/bruin_repository/send_initial_email_milestone_notification.md)
    * If send email is not Ok:
      ```
      self._logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket" f" {ticket_id}!")
      ```
    * Else:
      * [_append_reminder_note](_append_reminder_note.md)
      * If append note is Ok:
        ```
        self._logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!")
        ```
* If status 473:
  ```
  self._logger.info(f"[{outage_type.value}] There is a resolve outage ticket for the same location of faulty "
                    f"edge {serial_number} (ticket ID = {ticket_id}). The ticket was "
                    f"automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was "
                    f"appended to it. Appending initial triage note for this service number...")
  ```
  * [_append_triage_note](_append_triage_note.md)
  * [_change_ticket_severity](_change_ticket_severity.md)
  * If should schedule hnoc forwarding:
    * [schedule_forward_to_hnoc_queue](schedule_forward_to_hnoc_queue.md)
  * Else:
    ```
    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
                        f"should not be forwarded to HNOC. Skipping forward to HNOC...")
    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                        f"with serial: {serial_number} instead of scheduling forward to HNOC...")
    ```
    * [send_initial_email_milestone_notification](../../repositories/bruin_repository/send_initial_email_milestone_notification.md)
    * If send email status is no Ok:
      ```
      self._logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket" f" {ticket_id}!")
      ```
    * Else:
      * [_append_reminder_note](_append_reminder_note.md)
      * If append note is not Ok:
        ```
        self._logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket"
                           f" {ticket_id}!")
        ```