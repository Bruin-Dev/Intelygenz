## Run ticket autoresolve for edge

```
self._logger.info(f"[ticket-autoresolve] Starting autoresolve for edge {serial_number}...")
```

* If serial number not in autoresolve serial whitelist:
  ```
  self._logger.info(f"[ticket-autoresolve] Skipping autoresolve for edge {serial_number} because its "
                    f"serial ({serial_number}) is not whitelisted.")
  ```
* [get_open_outage_tickets](../../repositories/bruin_repository/get_open_outage_tickets.md)
  ```
  self._logger.info(f"Bad status calling for outage tickets for client id: {client_id} and serial: {serial_number}. "
                    f"Skipping autoresolve ...")
  ```
* If not found outage tickets:
  ```
  self._logger.info(f"[ticket-autoresolve] No outage ticket found for edge {serial_number}. " 
                    f"Skipping autoresolve...")
  ```
* If ticket not created by automation:
  ```
  self._logger.info(f"Ticket {outage_ticket_id} was not created by Automation Engine. Skipping autoresolve...")
  ```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
  ```
  self._logger.info(f"Bad status calling get ticket details for outage ticket: {outage_ticket_id}. "
                    f"Skipping autoresolve ...")
  ```
* If has faulty BYOB link and is ticket task in ipa queue:
  ```
  self._logger.info(f"Task for serial {serial_number} in ticket {outage_ticket_id} is related to a BYOB link "
                    f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions...")
  ```
* Else:
    * If was last outage detect recently:
      ```
      self._logger.info(f"Edge {serial_number} has been in outage state for a long time, so detail {ticket_detail_id} "
                          f"(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping "
                          f"autoresolve...")
      ```
    * If can't autoresolve one time more:
      ```
      self._logger.info(f"[ticket-autoresolve] Limit to autoresolve detail {ticket_detail_id} (serial {serial_number}) "
                          f"of ticket {outage_ticket_id} linked to edge {serial_number} has been maxed out already. "
                          "Skipping autoresolve...")
      ```
* If is detail resolved:
  ```
  self._logger.info(f"Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} is already "
                  "resolved. Skipping autoresolve...")
  ```
* If not PRODUCTION:
  ```
  self._logger.info(f"[ticket-autoresolve] Skipping autoresolve for edge {serial_number} since the "
                    f"current environment is {working_environment.upper()}.")
  ```

```
self._logger.info(f"Autoresolving detail {ticket_detail_id} of ticket {outage_ticket_id} linked to edge "
                  f"{serial_number} with serial number {serial_number}...")
```

* [unpause_ticket_detail](../../repositories/bruin_repository/unpause_ticket_detail.md)
* [resolve_ticket](../../repositories/bruin_repository/resolve_ticket.md)
  ```
  self._logger.warning(f"Bad status calling resolve ticket for outage ticket_id: {outage_ticket_id} and"
                       f"ticket detail: {ticket_detail_id}. Skipping autoresolve ...")
  ```
* [append_autoresolve_note_to_ticket](../../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)

```
self._logger.info(
                f"Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} linked to "
                f"edge {serial_number} was autoresolved!"
            )
  ```