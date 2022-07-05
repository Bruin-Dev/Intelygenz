## Get ticket details with and without triage
* For ticket in tickets:
  ```
  self._logger.info(f"Checking details of ticket_id: {ticket_id}")
  ```
  * For detail in ticket details:
    ```
    self._logger.info(
                    f"Checking for triage notes in ticket_id: {ticket_id} "
                    f"relating to serial number: {serial_number}"
                )
    ```
    * If notes related to serial:
      ```
      self._logger.info(
                        f"No triage notes found in ticket_id: {ticket_id} "
                        f"for serial number {serial_number}. "
                        f"Adding to ticket_details_without_triage list..."
                    )
      ```
    * Else:
      ```
      sself._logger.info(
                        f"Triage note found in ticket_id: {ticket_id} "
                        f"for serial number {serial_number}. "
                        f"Adding to ticket_details_with_triage list..."
                    )
      ```