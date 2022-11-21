## Filter outage ticket details based on last outage
* for ticket detail in tickets details:
  * If is outage ticket and last outage detected recently:
    ```
    self._logger.info(
                        f"Last outage detected for serial {serial_number} in Service Outage ticket {ticket_id} is "
                        "too recent. Skipping..."
                    )
    ```