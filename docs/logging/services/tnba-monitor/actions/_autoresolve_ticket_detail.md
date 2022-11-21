## Autoresolve ticket detail
```
self._logger.info(f"Running autoresolve for serial {serial_number} of ticket {ticket_id}...")
```
* If ticket created by automation engine:
  ```
  self._logger.info(
                f"Ticket {ticket_id}, where serial {serial_number} is, was not created by Automation Engine. "
                "Skipping autoresolve..."
            )
  ```
* If is detail in outage ticket:
  ```
  self._logger.info(
                f"Serial {serial_number} of ticket {ticket_id} is in outage state. Skipping autoresolve..."
            )
  ```
* If is detail in affecting ticket and are all metrics within thresholds:
  ```
  self._logger.info(
                f"At least one metric from serial {serial_number} of ticket {ticket_id} is not within the threshold."
                f" Skipping autoresolve..."
            )
  ```
* If prediction is not confident enough:
  ```
  self._logger.info(
                f"The confidence of the best prediction found for ticket {ticket_id}, where serial {serial_number} is, "
                f"did not exceed the minimum threshold. Skipping autoresolve..."
            )
  ```
* If environment is not PRODUCTION:
  ```
  self._logger.info(
                f"Detail related to serial {serial_number} of ticket {ticket_id} was about to be resolved, but the "
                f"current environment is {self._config.CURRENT_ENVIRONMENT.upper()}. Skipping autoresolve..."
            )
  ```
* [unpause_ticket_detail](../repositories/bruin_repository/unpause_ticket_detail.md)
* [resolve_ticket_detail](../repositories/bruin_repository/resolve_ticket_detail.md)
* If resolve ticket detail status is not Ok:
  ```
  self._logger.warning(f"Bad status calling resolve ticket detail for ticket id: {ticket_id} "
                                 f"and ticket detail id: {ticket_detail_id} . Skipping resolve ticket detail")
  ```