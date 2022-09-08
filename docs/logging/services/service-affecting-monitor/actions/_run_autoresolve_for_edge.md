## Run autoresolve for edge Documentation

```
self._logger.info(f"Starting autoresolve for edge {serial_number}...")
```

* if all_metrics_within_thresholds is empty
  ```
   self._logger.info(
                    f"At least one metric of edge {serial_number} is not within the threshold. Skipping autoresolve..."
                )
  ```
* [Get open affecting tickets](../repositories/bruin_repository/get_open_affecting_tickets.md)

* if affecting tickets is empty
  ```
  self._logger.info(
                    f"No affecting ticket found for edge with serial number {serial_number}. Skipping autoresolve..."
                )
  ```
* for affecting_ticket in affecting_tickets
  * if not was_ticket_created_by_automation_engine
    ```                
    self._logger.info(f"Ticket {affecting_ticket_id} was not created by Automation Engine. Skipping autoresolve...")
    ```
  * [Get ticket details](../repositories/bruin_repository/get_ticket_details.md)
  * if remove_auto_resolution_restrictions_for_byob
    ```
    self._logger.info(
                      f"Task for serial {serial_number} in ticket {affecting_ticket_id} is related to a BYOB link "
                      f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions..."
                    )
    ```
  * else
    * if not last_trouble_was_detected_recently
      ```
      self._logger.info(
                        f"Edge with serial number {serial_number} has been under an affecting trouble for a long "
                        f"time, so the detail of ticket {affecting_ticket_id} related to it will not be "
                        f"autoresolved. Skipping autoresolve..."
                        )
      ```
    * if is_autoresolve_threshold_maxed_out
      ```
      self._logger.info(
                        f"Limit to autoresolve detail of ticket {affecting_ticket_id} related to serial "
                        f"{serial_number} has been maxed out already. Skipping autoresolve..."
                        )
      ```
  * if is_task_resolved
    ```
    self._logger.info(
                        f"Detail of ticket {affecting_ticket_id} related to serial {serial_number} is already "
                        "resolved. Skipping autoresolve..."
                    )
    ```
  * if working_environment != "production"
    ```
    self._logger.info(
                        f"Skipping autoresolve for detail of ticket {affecting_ticket_id} related to serial number "
                        f"{serial_number} since the current environment is {working_environment.upper()}"
                    )
    ```
  
  ```
  self._logger.info(
                    f"Autoresolving detail of ticket {affecting_ticket_id} related to serial number {serial_number}..."
                )
  ```
  * [Unpause ticket detail](../repositories/bruin_repository/unpause_ticket_detail.md)
  * [Resolve ticket](../repositories/bruin_repository/resolve_ticket.md)
  * [Append autoresolve note to ticket](../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)
  ```
  self._logger.info(
                    f"Detail of ticket {affecting_ticket_id} related to serial number {serial_number} was autoresolved!"
                )
  ```
  
``` 
self._logger.info(f"Finished autoresolve for edge {serial_number}!")
```