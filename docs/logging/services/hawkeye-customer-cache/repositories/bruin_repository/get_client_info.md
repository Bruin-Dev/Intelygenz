## Get client info for device

```python
logger.info(f"Claiming client info for service number {service_number}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when claiming client info for service number {service_number} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got client info for service number {service_number}!")
```

* If response status for get client info for device is not ok:
  ```python
  err_msg = (
      f"Error while claiming client info for service number {service_number} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```