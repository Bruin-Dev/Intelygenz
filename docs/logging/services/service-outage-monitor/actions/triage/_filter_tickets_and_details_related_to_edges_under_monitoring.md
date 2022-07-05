## Filter tickets and details related to edges under monitoring
* For ticket in tickets:
  ```
  self._logger.info(f'Checking ticket_id: {ticket["ticket_id"]} for relevant details')
  ```
  * If not relevant details:
    ```
    self._logger.info(f'Ticket with ticket_id: {ticket["ticket_id"]} has no relevant details')
    ```
  ```
  self._logger.info(
                f'Ticket with ticket_id: {ticket["ticket_id"]} contains relevant details.'
                f"Appending to relevant_tickets list ..."
            )
  ```