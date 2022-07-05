## Get next results for ticket detail
```
self._logger.info(
                f"Claiming next results for ticket {ticket_id}, detail {detail_id} and "
                f"service number {service_number}..."
            )
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when claiming next results for ticket {ticket_id}, detail {detail_id} and "
                f"service number {service_number} -> {e}")
  ```
```
self._logger.info(
                f"Got next results for ticket {ticket_id}, detail {detail_id} and service number {service_number}!"
            )
```
* If status not 200:
  ```
  self._logger.error(f"Error while claiming next results for ticket {ticket_id}, detail {detail_id} and "
                    f"service number {service_number} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```