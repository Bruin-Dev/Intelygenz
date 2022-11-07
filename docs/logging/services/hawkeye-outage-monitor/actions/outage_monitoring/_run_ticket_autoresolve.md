## Run ticket task auto-resolve for online Ixia device

```python
logger.info(f"Starting autoresolve for device {serial_number}...")
```

[BruinRepository::get_open_outage_tickets](../../repositories/bruin_repository/get_open_outage_tickets.md)

* If response status for get open Service Outage tickets is not ok:
  ```python
  logger.error(
      f"Error while getting open Service Outage tickets for device {serial_number}: "
      f"{outage_ticket_response}. Skipping autoresolve..."
  )
  ```
  END

* If there are no open tickets for the Ixia device:
  ```python
  logger.warning(f"No open outage ticket found for device {serial_number}. Skipping autoresolve...")
  ```
  END

* If the existing Service Outage ticket was not created by the IPA system:
  ```python
  logger.warning(
      f"Ticket {outage_ticket_id} was not created by Automation Engine. Skipping autoresolve..."
  )
  ```
  END

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {outage_ticket_id}: {ticket_details_response}. "
      f"Skipping autoresolve..."
  )
  ```
  END

* If the last outage documented in the ticket took place long time ago:
  ```python
  logger.warning(
      f"Device {device} has been in outage state for a long time, so detail {client_id} "
      f"(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping "
      f"autoresolve..."
  )
  ```
  END

* If the number of allowed auto-resolves has been maxed out for the task linked to the Ixia device:
  ```python
  logger.warning(
      f"Limit to autoresolve ticket {outage_ticket_id} linked to device "
      f"{serial_number} has been maxed out already. Skipping autoresolve..."
  )
  ```
  END

* If the task linked to the Ixia device is already resolved:
  ```python
  logger.warning(
      f"Task for {serial_number} of ticket {outage_ticket_id} is already resolved. "
      f"Skipping autoresolve..."
  )
  ```
  END

```python
logger.info(f"Autoresolving task for device {serial_number} of ticket {outage_ticket_id}...")
```

[BruinRepository::unpause_ticket_detail](../../repositories/bruin_repository/unpause_ticket_detail.md)

[BruinRepository::resolve_ticket](../../repositories/bruin_repository/resolve_ticket.md)

* If response status for resolve ticket task is not ok:
  ```python
  logger.error(
      f"Error while resolving task for device {device} of ticket {outage_ticket_id}. "
      f"Skipping autoresolve ..."
  )
  ```
  END

[BruinRepository::append_autoresolve_note_to_ticket](../../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)

```python
logger.info(f"Task for device {serial_number} of ticket {outage_ticket_id} was autoresolved!")
```