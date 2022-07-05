## Create Affecting ticket Documentation

```
self._logger.info(
                f"Creating affecting ticket for serial {service_number} belonging to client {client_id}..."
            )
```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred while creating affecting ticket for client id {client_id} and serial "
                f"{service_number} -> {e}"
            )
  ```

* if response_status in range(200, 300)
  ```
  self._logger.info(
                    f"Affecting ticket for client {client_id} and serial {service_number} created successfully!"
                )
  ```
* else
  ```
  self._logger.error(
                    f"Error while opening affecting ticket for client {client_id} and serial {service_number} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )
  ```

