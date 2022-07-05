## Create outage ticket
```
self._logger.info(
            f"Attempting outage ticket creation for client_id {client_id}, " f"and circuit_id {circuit_id}"
        )
```
* If not PRODUCTION:
  ```
  self._logger.info(
                f"No outage ticket will be created for client_id {client_id} and circuit_id {circuit_id} "
                f"since the current environment is not production"
            )
  ```
* [create_outage_ticket](../repositories/bruin_repository/create_outage_ticket.md)
```
self._logger.info(
            f"Bruin response for ticket creation for edge with circuit id {circuit_id}: " f"{outage_ticket_response}"
        )
```
* If status is Ok:
  ```
  self._logger.info(f"Successfully created outage ticket with ticket_id {outage_ticket_body}")
  ```
* If is custom status:
  ```
  self._logger.info(
                f"Ticket for circuit id {circuit_id} already exists with ticket_id {outage_ticket_body}."
                f"Status returned was {outage_ticket_status}"
            )
  ```
  * If status = 409:
    ```
    self._logger.info(f"In Progress ticket exists for location of circuit id {circuit_id}")
    ```
  * If status = 472:
    ```
    self._logger.info(f"Resolved ticket exists for circuit id {circuit_id}")
    ```
  * If status = 473:
    ```
    self._logger.info(f"Resolved ticket exists for location of circuit id {circuit_id}")
    ```
* If dri paramas:
  ```
  self._logger.info(
                f"Appending InterMapper note to ticket id {outage_ticket_body} with dri parameters: "
                f"{dri_parameters}"
            )
  ```
  * [append_dri_note](../repositories/bruin_repository/append_dri_note.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling append dri note. Skipping create outage ticket ...")
    ```
```
self._logger.info(f"Appending InterMapper note to ticket id {outage_ticket_body}")
```
* [append_intermapper_note](../repositories/bruin_repository/append_intermapper_note.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling append intermapper note. Skipping create outage ticket ...")
  ```