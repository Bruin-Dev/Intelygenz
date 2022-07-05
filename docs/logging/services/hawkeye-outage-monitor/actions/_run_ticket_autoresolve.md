## Run ticket autoresolve
```
self._logger.info(f"Starting autoresolve for device {serial_number}...")
```
* [get_open_outage_tickets](../repositories/bruin_repository/get_open_outage_tickets.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to get open outage tickets. "
                                     f"Skipping run ticket autoresolve ...")
  ```
* If not outage tickets:
  ```
  self._logger.info(
                    f"No open outage ticket found for device {serial_number}. " f"Skipping autoresolve..."
                )
  ```
* If ticket created by automation:
  ```
  self._logger.info(
                    f"Ticket {outage_ticket_id} was not created by Automation Engine. Skipping autoresolve..."
                )
  ```
* [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)
* If status not Ok:
  ```
  self._logger.warning(f"Bad status calling to get ticket details. "
                                     f"Skipping run ticket autoresolve ...")
  ```
* If was last outage detected recently:
  ```
  self._logger.info(
                    f"Device {device} has been in outage state for a long time, so detail {client_id} "
                    f"(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping "
                    f"autoresolve..."
                )
  ```
* If can't ticket be autoresolve one more time:
  ```
  self._logger.info(
                    f"Limit to autoresolve ticket {outage_ticket_id} linked to device "
                    f"{serial_number} has been maxed out already. Skipping autoresolve..."
                )
  ```
* If detail is resolved:
  ```
  self._logger.info(
                    f"Detail {ticket_detail_id} of ticket {outage_ticket_id} is already resolved. "
                    f"Skipping autoresolve..."
                )
  ```
* If working environment PRODUCTION:
  ```
  self._logger.info(
                    f"Skipping autoresolve for device {serial_number} since the "
                    f"current environment is {working_environment.upper()}."
                )
  ```
```
self._logger.info(
                f"Autoresolving detail {ticket_detail_id} (serial: {serial_number}) of ticket {outage_ticket_id}..."
            )
```
* [unpause_ticket_detail](../repositories/bruin_repository/unpause_ticket_detail.md)
* [resolve_ticket](../repositories/bruin_repository/resolve_ticket.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling resolve ticket. Skipping autoresolve ...")
  ```
* [append_autoresolve_note_to_ticket.md](../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)
```
self._logger.info(f"Ticket {outage_ticket_id} linked to device {serial_number} was autoresolved!")
```