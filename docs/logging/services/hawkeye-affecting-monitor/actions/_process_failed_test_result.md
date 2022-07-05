## Process failed test result
```
self._logger.info(
            f"Processing FAILED test result {test_result_id} (type: {test_type}) that was run for serial "
            f"{serial_number}..."
        )
```
* If serial not in tickets:
  ```
  self._logger.info(
                f"Serial {serial_number} could not be added to the tickets mapping at the beginning of the "
                f"process, so the current FAILED state for test type {test_type} will be ignored. Skipping..."
            )
  ```
* If not affecting ticket:
  * If working environment is not PRODUCTION:
    ```
    self._logger.info(
                    f"Serial {serial_number} is not under any affecting ticket and some troubles were spotted for "
                    f"test type {test_type}, but the current environment is not PRODUCTION. Skipping ticket creation..."
                )
    ```
  ```
  self._logger.info(
                f"Serial {serial_number} is not under any affecting ticket and some troubles were spotted for "
                f"test type {test_type}. Creating affecting ticket.."
            )
  ```
  * [create_affecting_ticket](../repositories/bruin_repository/create_affecting_ticket.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"Bad status calling create affecting ticket to serial: {serial_number}."
                                     f"Skipping process test failed ...")
    ```
  ```
  self._logger.info(
                f"Affecting ticket created for serial {serial_number} (ID: {ticket_id}). A new note reporting the "
                f"current FAILED state for test type {test_type} will be built and appended to the ticket later on."
            )
  ```
* Else:
  ```
  self._logger.info(
                f"Serial {serial_number} is under affecting ticket {ticket_id} and some troubles were spotted for "
                f"test type {test_type}."
            )
  ```
  * If detail resolved ticket:
    ```
    self._logger.info(
                    f"Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} is "
                    f"currently unresolved and a FAILED state was spotted. Unresolving detail..."
                )
    ```
    * [unresolve_ticket_detail](../repositories/bruin_repository/unresolve_ticket_detail.md)
    * If status is not Ok:
      ```
      self._logger.info(
                        f"Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} "
                        "could not be unresolved. A note reporting the spotted FAILED state will be built and "
                        "appended to the ticket later on."
                    )
      ```
    * Else:
      ```
      self._logger.info(
                        f"Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} "
                        "was unresolved successfully. A note reporting the spotted FAILED state will be built and "
                        "appended to the ticket later on."
                    )
      ```
  * If not last note:
    ```
    self._logger.info(
                    f"No note was found for serial {serial_number} and test type {test_type} in ticket {ticket_id}. "
                    "A new note reporting the current FAILED state for this test type will be built and appended "
                    "to the ticket later on."
                )
    ```
  * Else:
    * If passed note:
      ```
      self._logger.info(
                        f"Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} "
                        f"corresponds to a PASSED state. A new note reporting the current FAILED state for this test "
                        "type will be built and appended to the ticket later on."
                    )
      ```
    * Else:
      ```
      self._logger.info(
                        f"Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} "
                        "corresponds to a previous FAILED state. No new notes will be built to report the current "
                        "FAILED state."
                    )
      ```
  ```
  self._logger.info(f"Finished processing FAILED test result {test_result_id}!")
  ```