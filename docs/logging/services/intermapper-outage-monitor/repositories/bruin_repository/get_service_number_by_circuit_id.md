## Get service number by circuit ID

```python
logger.info(f"Getting the translation to service number for circuit_id {circuit_id}")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"Getting the translation to service number for circuit_id {circuit_id} Error: {e}"
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get service number by circuit ID is not ok or is `204`:
  ```python
  err_msg = (
      f"Getting the translation to service number for circuit_id {circuit_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```