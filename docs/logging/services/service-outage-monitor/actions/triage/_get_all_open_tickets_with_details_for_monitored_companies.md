## Get all open tickets with details for monitored companies
* [get_open_outage_tickets](../../repositories/bruin_repository/get_open_outage_tickets.md)
* If get open outage status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to open tickets. Return an empty list ...")
  ```
```
self._logger.info("Getting all opened tickets details for each open ticket ...")
```
* [_get_open_tickets_with_details_by_ticket_id](_get_open_tickets_with_details_by_ticket_id.md)
```
self._logger.info("Finished getting all opened ticket details!")
```
