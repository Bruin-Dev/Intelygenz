## Autoresolve ticket
```
self._logger.info("Starting the autoresolve process")
```
* [get_ticket_basic_info](../repositories/bruin_repository/get_ticket_basic_info.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to get ticket basic info for client id:  {client_id}."
                                 f"Skipping autoresolve ticket ...")
  ```
```
self._logger.info(f"Found {len(tickets_body)} tickets for circuit ID {circuit_id} from bruin:")
self._logger.info(tickets_body)
```
* For ticket in tickets:
  ```
  self._logger.info(
                f"Posting InterMapper UP note to task of ticket id {ticket_id} "
                f"related to circuit ID {circuit_id}..."
            )
  ```
  * [_append_intermapper_up_note](../repositories/bruin_repository/append_intermapper_up_note.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling to append intermapper note to ticket id: {ticket_id}."
                                     f"Skipping autoresolve ticket ....")
    ```
  * [get_tickets](../repositories/bruin_repository/get_tickets.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling to get ticket for client id: {client_id} and "
                                     f"ticket id: {ticket_id}. Skipping autoresolve ticket ...")
    ```
  * If no product category:
    ```
    self._logger.info(f"Ticket {ticket_id} couldn't be found in Bruin. Skipping autoresolve...")
    ```
  ```
  self._logger.info(f"Product category of ticket {ticket_id} from bruin is {product_category}")
  ```
  * If product category whitelisted:
    ```
    self._logger.info(
                    f"At least one product category of ticket {ticket_id} from the "
                    f"following list is not one of the whitelisted categories for "
                    f"auto-resolve: {product_category}. Skipping autoresolve ..."
                )
    ```
  ```
  self._logger.info(f"Checking to see if ticket {ticket_id} can be autoresolved")
  ```
  * [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling get ticket details to ticket id: {ticket_id}."
                                     f"Skipping autoresolve ...")
    ```
  * If not detected outage recently:
    ```
    self._logger.info(
                    f"Edge has been in outage state for a long time, so detail {ticket_detail_id} "
                    f"(circuit ID {circuit_id}) of ticket {ticket_id} will not be autoresolved. Skipping "
                    f"autoresolve..."
                )
    ```
  * If can't autoresolve one more time:
    ```
    self._logger.info(
                    f"Limit to autoresolve detail {ticket_detail_id} (circuit ID {circuit_id}) "
                    f"of ticket {ticket_id} has been maxed out already. "
                    "Skipping autoresolve..."
                )
    ```
  * If detail is resolved:
    ```
    self._logger.info(
                    f"Detail {ticket_detail_id} (circuit ID {circuit_id}) of ticket {ticket_id} is already "
                    "resolved. Skipping autoresolve..."
                )
    ```
  * If curren environment is not production:
    ```
    self._logger.info(
                    f"Skipping autoresolve for circuit ID {circuit_id} "
                    f"since the current environment is not production"
                )
    ```
  * [unpause_ticket_detail](../repositories/bruin_repository/unpause_ticket_detail.md)
  * [resolve_ticket](../repositories/bruin_repository/resolve_ticket.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling to resolve ticket: {ticket_id}. Skipping autoresolve ...")
    ```
  ```
  self._logger.info(
                f"Autoresolve was successful for task of ticket {ticket_id} related to "
                f"circuit ID {circuit_id}. Posting autoresolve note..."
            )
  ```
  * [append_autoresolve_note_to_ticket](../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)
  ```
  self._logger.info(
                f"Detail {ticket_detail_id} (circuit ID {circuit_id}) of ticket {ticket_id} " f"was autoresolved!"
            )
  ```