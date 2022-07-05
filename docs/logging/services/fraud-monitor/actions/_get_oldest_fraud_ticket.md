## Get oldest fraud ticket
* For ticket in tickets:
  * [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling to get ticket details for ticket id: {ticket_id}."
                                     f"Skipping get oldest fraud ticket ...")
    ```