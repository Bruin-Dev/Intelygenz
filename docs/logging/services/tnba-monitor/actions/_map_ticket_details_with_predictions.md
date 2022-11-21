## Map ticket details with predictions
* for detail obj in detail ticket details:
  * If not predictions for ticket:
    ```
    self._logger.info(
                    f"Ticket {ticket_id} does not have any prediction associated. Skipping serial "
                    f"{serial_number}..."
                )
    ```
  * If not prediction object for related serial:
    ```
    self._logger.info(
                    f"No predictions were found for ticket {ticket_id} and serial {serial_number}. Skipping..."
                )
    ```