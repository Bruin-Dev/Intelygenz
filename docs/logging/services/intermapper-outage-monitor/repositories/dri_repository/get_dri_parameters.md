## Get DRI parameters

```python
logger.info(f"Getting DRI parameters of serial number {serial_number}")
```

* If there's an error while asking for the data to the `dri-bridge`:
  ```python
  err_msg = f"An error occurred while getting DRI parameter for serial number {serial_number}. Error: {e}"
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get DRI parameters is not ok:
  ```python
  err_msg = (
      f"Error while getting DRI parameter of serial number {serial_number} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
* Otherwise:
  ```python
  logger.info(f"Got DRI parameter of serial number {serial_number}!")
  ```