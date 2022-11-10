## Run Auto-Resolve for tickets related to an edge whose links have stabilized

```python
logger.info(f"Starting autoresolve for edge {serial_number}...")
```

* If not all links' metrics are within the thresholds:
  ```python
  logger.warning(
      f"At least one metric of edge {serial_number} is not within the threshold. Skipping autoresolve..."
  )
  ```
  END

[BruinRepository::get_open_affecting_tickets](../../repositories/bruin_repository/get_open_affecting_tickets.md)

* If response status for get open Service Affecting tickets is not ok:
  ```python
  logger.error(
      f"Error while getting open Service Affecting tickets for edge {serial_number}: "
      f"{affecting_ticket_response}. Skipping autoresolve..."
  )
  ```
  END

* If no open Service Affecting tickets were found for the edge:
  ```python
  logger.warning(
      f"No affecting ticket found for edge with serial number {serial_number}. Skipping autoresolve..."
  )
  ```
  END

* For each open Service Affecting ticket found for the edge:

    * If the ticket was not created by the IPA system:
      ```python
      logger.warning(
          f"Ticket {affecting_ticket_id} was not created by Automation Engine. Skipping autoresolve..."
      )
      ```
      _Continue with next ticket_

    [BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

    * If response status for get ticket details is not ok:
      ```python
      logger.error(
          f"Error while getting details of ticket {affecting_ticket_id}: "
          f"{ticket_details_response}. Skipping autoresolve..."
      )
      ```
      _Continue with next ticket_

    * If the trouble reported to the ticket is related to a BYOB link, and the ticket task is sitting in the IPA queue:
      ```python
      logger.info(
          f"Task for serial {serial_number} in ticket {affecting_ticket_id} is related to a BYOB link "
          f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions..."
      )
      ```
    * Otherwise:

        * If the last trouble was reported to the ticket long time ago:
          ```python
          logger.warning(
              f"Edge with serial number {serial_number} has been under an affecting trouble for a long "
              f"time, so the detail of ticket {affecting_ticket_id} related to it will not be "
              f"autoresolved. Skipping autoresolve..."
          )
          ```
         _Continue with next ticket_

        * If the max number of auto-resolves has been reached for the ticket task related to the edge:
          ```python
          logger.warning(
              f"Limit to autoresolve detail of ticket {affecting_ticket_id} related to serial "
              f"{serial_number} has been maxed out already. Skipping autoresolve..."
          )
          ```
          _Continue with next ticket_

      * If the ticket task related to the edge is already resolved:
        ```python
        logger.warning(
            f"Detail of ticket {affecting_ticket_id} related to serial {serial_number} is already "
            "resolved. Skipping autoresolve..."
        )
        ```
        _Continue with next ticket_
    
      ```python
      logger.info(
          f"Autoresolving detail of ticket {affecting_ticket_id} related to serial number {serial_number}..."
      )
      ```

      [BruinRepository::unpause_ticket_detail](../../repositories/bruin_repository/unpause_ticket_detail.md)

      [BruinRepository::resolve_ticket](../../repositories/bruin_repository/resolve_ticket.md)

      * If response status for resolve ticket task is not ok:
        ```python
        logger.error(
            f"Error while resolving ticket task of ticket {affecting_ticket_id} for edge {serial_number}: "
            f"{resolve_ticket_response}. Skipping autoresolve..."
        )
        ```
        _Continue with next ticket_

      [BruinRepository::append_autoresolve_note_to_ticket](../../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)

      ```python
      logger.info(
          f"Detail of ticket {affecting_ticket_id} related to serial number {serial_number} was autoresolved!"
      )
      ```

      * If there was any task scheduled to forward a ticket task to HNOC:
        ```python
        logger.info(
            f"Removed scheduled task to forward to {ForwardQueues.HNOC.value} "
            f"for autoresolved ticket {affecting_ticket_id} and serial number {serial_number}"
        )
        ```

```python
logger.info(f"Finished autoresolve for edge {serial_number}!")
```