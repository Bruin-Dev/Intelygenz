## Create outage ticket

```python
logger.info(
    f"Attempting outage ticket creation for client_id {client_id} and service_number {service_number}"
)
```

* If environment is not `PRODUCTION`:
  ```python
  logger.info(
      f"No outage ticket will be created for client_id {client_id} and circuit_id {circuit_id} "
      f"since the current environment is not production"
  )
  ```
  END

[create_outage_ticket](../repositories/bruin_repository/create_outage_ticket.md)

```python
logger.info(
    f"Bruin response for ticket creation for service number {service_number}: {outage_ticket_response}"
)
```

* If response status for ticket creation is ok:
  ```python
  logger.info(f"Successfully created outage ticket with ticket_id {ticket_id}")
  ```

* If response status for ticket creation is a Bruin custom status (`409`, `472` or `473`):
    ```python
    logger.info(
        f"Ticket for service number {service_number} already exists with ticket_id {ticket_id}."
        f"Status returned was {outage_ticket_status}"
    )
    ```

    * If response status for ticket creation is `409`:
      ```python
      logger.info(f"In Progress ticket exists for location of service number {service_number}")
      ```

    * If response status for ticket creation is `472`:
      ```python
      logger.info(f"Resolved ticket exists for service number {service_number}")
      ```

    * If response status for ticket creation is `473`:
      ```python
      logger.info(f"Resolved ticket exists for location of service number {service_number")
      ```

* If response status for get ticket details is not ok:
    ```python
    logger.warning(
        f"Bad status calling get ticket details to ticket id: {ticket_id}. Skipping append note to ticket..."
    )
    ```
    
* If current condition has already been reported on the ticket:
    ```python
    logger.info(
        f"Current condition has already been reported on ticket id {ticket_id}. "
        f"Skipping append note to ticket..."
    )
    ```

* If additional data exists in the DRI system for service number:
    ```python
    logger.info(
        f"Appending InterMapper note to ticket id {ticket_id} with dri parameters: "
        f"{dri_parameters}"
    )
    ```
    [append_dri_note](../repositories/bruin_repository/append_dri_note.md)
    * If response status for append DRI note to ticket is not ok:
      ```python
      logger.warning(f"Bad status calling append dri note. Skipping append note to ticket...")
      ```
    * Otherwise:

        END

* Otherwise:
    ```python
    logger.info(f"Appending InterMapper note to ticket id {ticket_id}")
    ```
    [append_intermapper_note](../repositories/bruin_repository/append_intermapper_note.md)
    * If response status of append InterMapper note is not ok:
      ```python
      logger.warning(f"Bad status calling append intermapper note. Skipping append note to ticket...")
      ```
      END

* If device should be forwarded to the `IPA Investigate` work queue:

    [_schedule_forward_to_queue](_schedule_forward_to_queue.md) (`IPA Investigate` queue)

    [_schedule_forward_to_queue](_schedule_forward_to_queue.md) (`HNOC Investigate` queue)