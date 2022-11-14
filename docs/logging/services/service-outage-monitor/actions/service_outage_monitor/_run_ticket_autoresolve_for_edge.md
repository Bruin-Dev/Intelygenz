## Auto-Resolve ticket task for edge

```python
logger.info(f"Starting autoresolve for edge {serial_number}...")
```

* If the edge is not whitelisted for auto-resolves:
  ```python
  logger.info(f"Skipping autoresolve for edge {serial_number} because its serial is not whitelisted")
  ```
  END

[BruinRepository::get_open_outage_tickets](../../repositories/bruin_repository/get_open_outage_tickets.md)

* If response status for get open Service Outage tickets is not ok:
  ```python
  logger.error(
      f"Error while getting open Service Outage tickets for edge {serial_number}: "
      f"{outage_ticket_response}. Skipping autoresolve..."
  )
  ```
  END

* If no open Service Outage tickets were found:
  ```python
  logger.info(f"No open Service Outage ticket found for edge {serial_number}. Skipping autoresolve...")
  ```
  END

* If the ticket was not created by the IPA system:
  ```python
  logger.info(
      f"Ticket {outage_ticket_id} for edge {serial_number} was not created by Automation Engine. "
      f"Skipping autoresolve..."
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

* If the outage reported to the ticket is related to a BYOB link, and the ticket task is sitting in the IPA queue:
  ```python
  logger.info(
      f"Task for serial {serial_number} in ticket {outage_ticket_id} is related to a BYOB link "
      f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions..."
  )
  ```
* Otherwise:

    * If the last outage was reported to the ticket long time ago:
      ```python
      logger.info(
          f"Edge {serial_number} has been in outage state for a long time, so the task from ticket "
          f"{outage_ticket_id} will not be autoresolved. Skipping autoresolve..."
      )
      ```
     END

    * If the max number of auto-resolves has been reached for the ticket task related to the edge:
      ```python
      logger.info(
          f"Limit to autoresolve task of ticket {outage_ticket_id} for edge {serial_number} "
          f"has been maxed out already. Skipping autoresolve..."
      )
      ```
      END

    * If the ticket task related to the edge is already resolved:
      ```python
      logger.info(
          f"Task of ticket {outage_ticket_id} for edge {serial_number} is already resolved. "
          f"Skipping autoresolve..."
      )
      ```
      END

```python
logger.info(f"Autoresolving task of ticket {outage_ticket_id} for edge {serial_number}...")
```

[BruinRepository::unpause_ticket_detail](../../repositories/bruin_repository/unpause_ticket_detail.md)

[BruinRepository::resolve_ticket](../../repositories/bruin_repository/resolve_ticket.md)

* If response status for resolve ticket task is not ok:
  ```python
  logger.error(
      f"Error while resolving task of ticket {outage_ticket_id} for edge {serial_number}: "
      f"{resolve_ticket_response}. Skipping autoresolve ..."
  )
  ```
  END

[BruinRepository::append_autoresolve_note_to_ticket](../../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)

```python
logger.info(f"Task of ticket {outage_ticket_id} for edge {serial_number} was autoresolved!")
```

* If there was any task scheduled to forward a ticket task to HNOC:
  ```python
  logger.info(
      f"Removed scheduled task to forward to {ForwardQueues.HNOC.value} "
      f"for auto-resolved task of ticket {outage_ticket_id} for edge {serial_number}"
  )
  ```