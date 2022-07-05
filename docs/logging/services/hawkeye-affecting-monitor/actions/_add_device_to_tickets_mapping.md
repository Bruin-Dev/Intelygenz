## Add device to tickets mapping
* [get_open_affecting_tickets](../repositories/bruin_repository/get_open_affecting_tickets.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to get open affecting ticket to serial number "
                                     f"{serial_number}. Skipping add device to ticket mapping ...")
  ```
* If not affecting ticket:
  ``` 
  self._logger.info(
                    f"No affecting tickets were found for device {serial_number} when building the mapping between "
                    f"this serial and tickets."
                )
  ```
* [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
  ```
  self._logger.warning(f"Bad status calling to get ticket details to ticket id: {ticket_id}."
                                     f"Skipping add devices to ticket mapping ...")
  ```