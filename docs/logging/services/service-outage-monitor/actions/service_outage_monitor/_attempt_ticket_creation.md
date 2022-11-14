## Try to create a Service Outage ticket for an edge

```python
logger.info(f"[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...")
```

[BruinRepository::create_outage_ticket](../../repositories/bruin_repository/create_outage_ticket.md)

```python
logger.info(
    f"[{outage_type.value}] Bruin response for ticket creation for edge {edge}: "
    f"{ticket_creation_response}"
)
```

* If response status for create Service Outage ticket is 200:
    ```python
    logger.info(
        f"[{outage_type.value}] Successfully created outage ticket for edge {edge}. Ticket ID: {ticket_id}"
    )
    ```

    [_append_triage_note](_append_triage_note.md)

    [_change_ticket_severity](_change_ticket_severity.md)

    * If the edge is under a Soft Down or Hard Down outage, or if the edge is under a Link Down outage and the disconnected links are not BYOB or Customer Provided:
        ```python
        logger.info(
            f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
            f"forwarded to the HNOC queue"
        )
        ```

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} "
            f"with link_data: {edge_links} has a blacklisted link and "
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

        * If response status for send initial e-mail milestone notification is not ok:
          ```python
          logger.error(
              f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
          )
          ```
        * Otherwise:

            [_append_reminder_note](_append_reminder_note.md)
    
            * If response status for append Reminder note to ticket is not ok:
            ```python
            logger.error(
                f"Reminder note of edge {serial_number} could not be appended to ticket"
                f" {ticket_id}!"
            )
            ```

    [_check_for_digi_reboot](_check_for_digi_reboot.md)

    END

* If response status for create Service Outage ticket is 409:
    ```python
    logger.info(
        f"[{outage_type.value}] Faulty edge {serial_number} already has an outage ticket in "
        f"progress (ID = {ticket_id}). Skipping outage ticket creation for "
        "this edge..."
    )
    ```

    [_change_ticket_severity](_change_ticket_severity.md)

    * If the edge is under a Soft Down or Hard Down outage, or if the edge is under a Link Down outage and the disconnected links are not BYOB or Customer Provided:
        ```python
        logger.info(
            f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
            f"forwarded to the HNOC queue"
        )
        ```

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} "
            f"with link_data: {edge_links} has a blacklisted link and "
            f"should not be forwarded to HNOC. Skipping forward to HNOC..."
        )
        ```

        [BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

        [_send_reminder](_send_reminder.md)

    [_check_for_failed_digi_reboot](_check_for_failed_digi_reboot.md)

    [_attempt_forward_to_asr](_attempt_forward_to_asr.md)

    END

* If response status for create Service Outage ticket is 471:
    ```python
    logger.info(
        f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
        f"(ID = {ticket_id}). Re-opening ticket..."
    )
    ```

    [_reopen_outage_ticket](_reopen_outage_ticket.md)

    [_change_ticket_severity](_change_ticket_severity.md)

    * If the edge is under a Soft Down or Hard Down outage, or if the edge is under a Link Down outage and the disconnected links are not BYOB or Customer Provided:
        ```python
        logger.info(
           f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
           f"forwarded to the HNOC queue"
        )
        ```

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} "
            f"with link_data: {edge_links} has a blacklisted link and "
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

        * If response status for send initial e-mail milestone notification is not ok:
          ```python
          logger.error(
              f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
          )
          ```
        * Otherwise:

            [_append_reminder_note](_append_reminder_note.md)
    
            * If response status for append Reminder note to ticket is not ok:
            ```python
            logger.error(
                f"Reminder note of edge {serial_number} could not be appended to ticket"
                f" {ticket_id}!"
            )
            ```

    [_check_for_digi_reboot](_check_for_digi_reboot.md)

    END

* If response status for create Service Outage ticket is 472:
    ```python
    logger.info(
        f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
        f"(ID = {ticket_id}). Its ticket detail was automatically unresolved "
        f"by Bruin. Appending reopen note to ticket..."
    )
    ```

    [_append_triage_note](_append_triage_note.md)

    [_change_ticket_severity](_change_ticket_severity.md)

    * If the edge is under a Soft Down or Hard Down outage, or if the edge is under a Link Down outage and the disconnected links are not BYOB or Customer Provided:
        ```python
        logger.info(
            f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
            f"forwarded to the HNOC queue"
        )
        ```

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} "
            f"with link_data: {edge_links} has a blacklisted link and "
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

        * If response status for send initial e-mail milestone notification is not ok:
          ```python
          logger.error(
              f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
          )
          ```
        * Otherwise:

            [_append_reminder_note](_append_reminder_note.md)
    
            * If response status for append Reminder note to ticket is not ok:
            ```python
            logger.error(
                f"Reminder note of edge {serial_number} could not be appended to ticket"
                f" {ticket_id}!"
            )
            ```

    END

* If response status for create Service Outage ticket is 473:
    ```python
    logger.info(
        f"[{outage_type.value}] There is a resolve outage ticket for the same location of faulty "
        f"edge {serial_number} (ticket ID = {ticket_id}). The ticket was "
        f"automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was "
        f"appended to it. Appending initial triage note for this service number..."
    )
    ```

    [_append_triage_note](_append_triage_note.md)

    [_change_ticket_severity](_change_ticket_severity.md)

    * If the edge is under a Soft Down or Hard Down outage, or if the edge is under a Link Down outage and the disconnected links are not BYOB or Customer Provided:
        ```python
        logger.info(
            f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
            f"forwarded to the HNOC queue"
        )
        ```

        [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    * Otherwise:
        ```python
        logger.info(
            f"Ticket_id: {ticket_id} for serial: {serial_number} "
            f"with link_data: {edge_links} has a blacklisted link and "
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

        * If response status for send initial e-mail milestone notification is not ok:
          ```python
          logger.error(
              f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
          )
          ```

        * Otherwise:

            [_append_reminder_note](_append_reminder_note.md)
    
            * If response status for append Reminder note to ticket is not ok:
            ```python
            logger.error(
                f"Reminder note of edge {serial_number} could not be appended to ticket"
                f" {ticket_id}!"
            )
            ```

    END