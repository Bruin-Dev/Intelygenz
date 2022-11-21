## Get open tickets with details by client id
* [get_open_outage_tickets](../repositories/bruin_repository/get_open_outage_tickets.md)
* If bad status calling to get outage tickets:
  ```
  self._logger.warning(f"Bad status calling to get outage tickets. Return empty list ...")
  ```
* [get_open_affecting_tickets](../repositories/bruin_repository/get_open_affecting_tickets.md)
  ```
  self._logger.warning(f"Bad status calling to get affecting tickets. Return empty list ...")
  ```
```
self._logger.info(f"Getting all opened tickets for Bruin customer {client_id}...")
```
* For ticket in all tickets:
  * [get_ticket_details.md](../repositories/bruin_repository/get_ticket_details.md)
    ```
    self._logger.warning(f"Bad status calling to get tickets details with id: {ticket_id}."
                                             f"Skipping ticket ...")
    ```
  * If not ticket details:
    ```
    self._logger.info(
                            f"Ticket {ticket_id} doesn't have any detail under ticketDetails key. " f"Skipping..."
                        )
    ```
  ```
  self._logger.info(f"Got details for ticket {ticket_id} of Bruin customer {client_id}!")
  self._logger.info(f"Finished getting all opened tickets for Bruin customer {client_id}!")
  ```
* If Exception:
  ```
  self._logger.error(
                f"An error occurred while trying to get open tickets with details for Bruin client {client_id} -> {e}"
            )
  ```