## Create Service Affecting ticket

```python
logger.info(f"Creating affecting ticket for serial {service_number} belonging to client {client_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred while creating affecting ticket for client id {client_id} and serial "
      f"{service_number} -> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for create Service Affecting ticket is not ok:
  ```python
  err_msg = (
      f"Error while opening affecting ticket for client {client_id} and serial {service_number} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
* Otherwise:
  ```python
  logger.info(
      f"Affecting ticket for client {client_id} and serial {service_number} created successfully!"
  )
  ```
