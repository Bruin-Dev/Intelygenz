## Process passed test result
```
self._logger.info(
            f"Processing PASSED test result {test_result_id} (type: {test_type}) that was run for serial "
            f"{serial_number}..."
        )
```
* If serial not in tickets:
  ```
  self._logger.info(
                f"Serial {serial_number} could not be added to the tickets mapping at the beginning of the "
                f"process, so the current PASSED state for test type {test_type} will be ignored. Skipping..."
            )
  ```
* If affecting tickets:
  ```
  self._logger.info(
                f"Serial {serial_number} is not under any affecting ticket and all thresholds are normal for "
                f"test type {test_type}. Skipping..."
            )
  ```
* If affecting ticket detail is solved:
  ```
  self._logger.info(
                f"Serial {serial_number} is under an affecting ticket (ID {ticket_id}) whose ticket detail is resolved "
                f"and all thresholds are normal for test type {test_type}, so the current PASSED state will not be "
                "reported. Skipping..."
            )
  ```
* If not last note:
  ```
  self._logger.info(
                f"No note was found for serial {serial_number} and test type {test_type} in ticket {ticket_id}. "
                "Skipping..."
            )
  ```
* If is passed note:
  ```
  self._logger.info(
                f"Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} "
                f"corresponds to a PASSED state. Skipping..."
            )
  ```
```
self._logger.info(
            f"Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} "
            "corresponds to a FAILED state. A new note reporting the current PASSED state will be built and appended "
            "to the ticket later on."
        )
self._logger.info(f"Finished processing PASSED test result {test_result_id}!")
```