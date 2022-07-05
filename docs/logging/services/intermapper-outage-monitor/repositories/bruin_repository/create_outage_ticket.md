## Create outage ticket Documentation
```
  self._logger.info(f"Creating outage ticket for device {service_number} that belongs to client {client_id}...")
  ```
* If Exception:
  ```
  self._logger.error(f"An error occurred when creating outage ticket for device {service_number} belong to client 
  {client_id} -> {e}")
  ```
```
self._logger.info(f"Outage ticket for device {service_number} that belongs to client {client_id} created!")
```
* If not a correct status
  ```
  self._logger.error(f"Error while creating outage ticket for device {service_number} that belongs to client "
                    f"{client_id} in {self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```