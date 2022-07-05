## Create fraud ticket
```
self._logger.info(
                f"Creating fraud ticket for service number {service_number} that belongs to client {client_id}..."
            )
```
* If Exception:
  ```
  f"An error occurred when creating fraud ticket for service number {service_number} "
                f"that belongs to client {client_id} -> {e}"
  ```
* If status ok:
  ```
  self._logger.info(f"Fraud ticket for service number {service_number} that belongs to client {client_id} created!")
  ```
* Else:
  ```
  self._logger.error(f"Error while creating fraud ticket for service number {service_number} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```