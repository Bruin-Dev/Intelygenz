## Get management status for device

```python
logger.info(f"Claiming management status for service number {service_number} and client {client_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when claiming management status for service number {service_number} and "
      f"client {client_id} -> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got management status for service number {service_number} and client {client_id}!")
```

* If response status for get management status for device is not ok:
  ```python
  err_msg = (
      f"Error while claiming management status for service number {service_number} and "
      f"client {client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```