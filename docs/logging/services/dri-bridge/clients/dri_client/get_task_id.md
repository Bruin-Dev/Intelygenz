## Create new task in DRI for serial number

```python
logger.info(f"Getting task id from serial {serial_number} with parameters {json_parameter_set}...")
```

Make a call to `GET /acs/device/{serial_number}/parameter_returnid?data={parameters}` with the specified query parameters.

* If there's an error while connecting to DRI API:
  ```python
  logger.error(f"An error occurred while trying to get the task id from serial {serial_number}")
  logger.error(f"Error: {err}")
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  logger.error(f"Got 401 from DRI. Re-logging in...")
  ```
  [login](login.md)

    END

* If the status of the HTTP response is `504`:
  ```python
  logger.error(f"Got {response.status}. Getting task_id of {serial_number} timed out")
  ```
  END

* If the status of the HTTP response is any other and not a `2xx`:
  ```python
  logger.error(f"Got {response.status}. Response returned {response_json}")
  ```
  END