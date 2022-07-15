## Create outage ticket

```python
self._logger.info(
    f"Attempting outage ticket creation for client_id {client_id} and service_number {service_number}"
)
```

* If environment is not `PRODUCTION`:
  ```python
  self._logger.info(
      f"No outage ticket will be created for client_id {client_id} and circuit_id {circuit_id} "
      f"since the current environment is not production"
  )
  ```
  END

[create_outage_ticket](../repositories/bruin_repository/create_outage_ticket.md)

```python
self._logger.info(
    f"Bruin response for ticket creation for service number {service_number}: {outage_ticket_response}"
)
```

* If response status for ticket creation is ok:
  ```python
  self._logger.info(f"Successfully created outage ticket with ticket_id {ticket_id}")
  ```

* If response status for ticket creation is a Bruin custom status (`409`, `472` or `473`):
    ```python
    self._logger.info(
        f"Ticket for service number {service_number} already exists with ticket_id {ticket_id}."
        f"Status returned was {outage_ticket_status}"
    )
    ```

    * If response status for ticket creation is `409`:
      ```python
      self._logger.info(f"In Progress ticket exists for location of service number {service_number}")
      ```

    * If response status for ticket creation is `472`:
      ```python
      self._logger.info(f"Resolved ticket exists for service number {service_number}")
      ```

    * If response status for ticket creation is `473`:
      ```python
      self._logger.info(f"Resolved ticket exists for location of service number {service_number")
      ```

* If additional data exists in the DRI system for service number:
    ```python
    self._logger.info(
        f"Appending InterMapper note to ticket id {ticket_id} with dri parameters: "
        f"{dri_parameters}"
    )
    ```
    [append_dri_note](../repositories/bruin_repository/append_dri_note.md)
    * If response status for append DRI note to ticket is not ok:
      ```python
      self._logger.warning(f"Bad status calling append dri note. Skipping create outage ticket ...")
      ```
    * Otherwise:

        END

* Otherwise:
    ```python
    self._logger.info(f"Appending InterMapper note to ticket id {ticket_id}")
    ```
    [append_intermapper_note](../repositories/bruin_repository/append_intermapper_note.md)
    * If response status of append InterMapper note is not ok:
      ```python
      self._logger.warning(f"Bad status calling append intermapper note. Skipping create outage ticket ...")
      ```
      END

* If device should be forwarded to the `IPA Investigate` work queue:
  * [_schedule_forward_to_queue](_schedule_forward_to_queue.md) (`IPA Investigate` queue)
  * [_schedule_forward_to_queue](_schedule_forward_to_queue.md) (`HNOC Investigate` queue)