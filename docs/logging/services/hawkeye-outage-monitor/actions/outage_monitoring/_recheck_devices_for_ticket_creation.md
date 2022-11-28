## Re-recheck devices sitting in the quarantine

```python
logger.info(f"Re-checking {len(devices)} devices in outage state prior to ticket creation...")
```

[HawkeyeRepository::get_probes](../../repositories/hawkeye_repository/get_probes.md)

* If response status for get Hawkeye's devices is not ok:
  ```python
  logger.error(f"Error while getting Hawkeye's probes: {probes_response}. Skipping re-check process...")
  ```
  END

* If there are no devices to re-check:
  ```python
  logger.warning("The list of probes arrived empty. Skipping re-check process...")
  ```
  END

* If there are no active devices to re-check:
  ```python
  logger.warning("All probes were detected as inactive. Skipping re-check process...")
  ```
  END

[_map_probes_info_with_customer_cache](_map_probes_info_with_customer_cache.md)

_The list of devices is split to two different data sets: devices in outage state and devices online_

* If there are devices still in outage state:
  ```python
  logger.info(
      f"{len(devices_still_in_outage)} devices were detected as still in outage state after re-check."
  )
  ```

    * For each device in outage state:
      ```python
      logger.info(f"Attempting outage ticket creation for faulty device {serial_number}...")
      ```

        [BruinRepository::create_outage_ticket](../../repositories/bruin_repository/create_outage_ticket.md)
          
        * If response status for create outage ticket is `200`:
            ```python
            logger.info(f"Outage ticket created for device {serial_number}! Ticket ID: {ticket_id}")
            ```

            ```python
            logger.info(f"Appending triage note to outage ticket {ticket_id}...")
            ```
            [BruinRepository::append_triage_note_to_ticket](../../repositories/bruin_repository/append_triage_note_to_ticket.md)

        * If response status for create outage ticket is `409`:
          ```python
          logger.info(
              f"Faulty device {serial_number} already has an outage ticket in progress (ID = {ticket_id})."
          )
          ```
          [_append_triage_note_if_needed](_append_triage_note_if_needed.md)

        * If response status for create outage ticket is `471`:
          ```python
          logger.info(
              f"Faulty device {serial_number} has a resolved outage ticket (ID = {ticket_id}). "
              "Re-opening ticket..."
          )
          ```
          [_reopen_outage_ticket](_reopen_outage_ticket.md)

        * If response status for create outage ticket is `472`:
          ```python
          logger.info(
              f"[outage-recheck] Faulty device {serial_number} has a resolved outage ticket "
              f"(ID = {ticket_id}). Its ticket detail was automatically unresolved "
              f"by Bruin. Appending reopen note to ticket..."
          )
          ```
          [BruinRepository::append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)

        * If response status for create outage ticket is `473`:
          ```python
          logger.info(
              f"[outage-recheck] There is a resolve outage ticket for the same location of faulty device "
              f"{serial_number} (ticket ID = {ticket_id}). The ticket was"
              f"automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was "
              f"appended to it. Appending initial triage note for this service number..."
          )
          ```
          [BruinRepository::append_triage_note_to_ticket](../../repositories/bruin_repository/append_triage_note_to_ticket.md)

* Otherwise:
  ```python
  logger.info("No devices were detected in outage state after re-check. Outage tickets won't be created")
  ```
  
* If there are devices online:
    ```python
    logger.info(f"{len(healthy_devices)} devices were detected in healthy state after re-check.")
    ```
    * For each online device:
  
        [_run_ticket_autoresolve](_run_ticket_autoresolve.md)

* Otherwise:
  ```python
  logger.info("No devices were detected in healthy state after re-check.")
  ```
  
```python
logger.info(f"Finished re-checking {len(devices)} devices")
```