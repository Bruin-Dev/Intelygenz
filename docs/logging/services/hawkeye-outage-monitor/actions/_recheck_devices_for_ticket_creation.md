## Recheck devices for ticket creation
```
self._logger.info(f"Re-checking {len(devices)} devices in outage state prior to ticket creation...")
```
* [get_probes](../repositories/hawkeye_repository/get_probes.md)
* If status not Ok:
  ```
  self._logger.warning(f"Bad status calling to get probes. Skipping hawkeye outage monitoring process ...")
  ```
* If not probes:
  ```
  self._logger.info("The list of probes arrived empty. Skipping monitoring process...")
  ```
* If not active probes:
  ```
  self._logger.info("All probes were detected as inactive. Skipping monitoring process...")
  ```
* [_map_probes_info_with_customer_cache](_map_probes_info_with_customer_cache.md)
* If environment not PRODUCTION:
  ```
  self._logger.info(
                f"Process cannot keep going as the current environment is {working_environment.upper()}. "
                f"Healthy devices: {len(healthy_devices)} | Outage devices: {len(devices_still_in_outage)}"
            )
  ```
* If devices still outage:
  ```
  self._logger.info(
                f"{len(devices_still_in_outage)} devices were detected as still in outage state after re-check."
            )
  ```
  * for device in devices:
    ```
    self._logger.info(f"Attempting outage ticket creation for faulty device {serial_number}...")
    ```
    * [create_outage_ticket](../repositories/bruin_repository/create_outage_ticket.md)
    * If create outage ticket status is Ok:
      ```
      self._logger.info(f"Outage ticket created for device {serial_number}! Ticket ID: {ticket_id}")
      self._logger.info(f"Appending triage note to outage ticket {ticket_id}...")
      ```
      * [append_triage_note_to_ticket](../repositories/bruin_repository/append_triage_note.md)
    * If create outage ticket status is 409:
      ```
      self._logger.info(
                        f"Faulty device {serial_number} already has an outage ticket in progress (ID = {ticket_id})."
                    )
      ```
      * [_append_triage_note_if_needed](_append_triage_note_if_needed.md)
    * If create outage ticket status is 471:
      ```
      self._logger.info(
                        f"Faulty device {serial_number} has a resolved outage ticket (ID = {ticket_id}). "
                        "Re-opening ticket..."
                    )
      ```
      * [_reopen_outage_ticket](_reopen_outage_ticket.md)
    * If create outage ticket status is 472:
      ```
      self._logger.info(
                        f"[outage-recheck] Faulty device {serial_number} has a resolved outage ticket "
                        f"(ID = {ticket_id}). Its ticket detail was automatically unresolved "
                        f"by Bruin. Appending reopen note to ticket..."
                    )
      ```
      * [append_note_to_ticket](../repositories/bruin_repository/append_note_to_ticket.md)
    * If create outage ticket status is 473:
      ```
      self._logger.info(
                        f"[outage-recheck] There is a resolve outage ticket for the same location of faulty device "
                        f"{serial_number} (ticket ID = {ticket_id}). The ticket was"
                        f"automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was "
                        f"appended to it. Appending initial triage note for this service number..."
                    )
      ```
      * [append_triage_note](../repositories/bruin_repository/append_note_to_ticket.md)
* Else: 
  ```
  self._logger.info(
                "No devices were detected in outage state after re-check. Outage tickets won't be created"
            )
  ```
* If healthy devices:
  ```
  self._logger.info(f"{len(healthy_devices)} devices were detected in healthy state after re-check.")
  ```
  * [_run_ticket_autoresolve](_run_ticket_autoresolve.md)
* Else:
  ```
  self._logger.info("No devices were detected in healthy state after re-check.")
  ```