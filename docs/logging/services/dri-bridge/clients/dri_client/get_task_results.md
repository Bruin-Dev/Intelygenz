## Get task results for serial number

```python
logger.info(f"Checking if {task_id} for serial {serial_number} is complete...")
```

Make a call to `GET /acs/device/{serial_number}/parameter_tid?transactionid={task_id}` with the specified query parameters.

* If there's an error while connecting to DRI API:
  ```python
  logger.error(f"An error occurred while checking if {task_id} for serial {serial_number} is complete")
  logger.error(f"Error: {err}")
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  logger.error(f"Got 401 from DRI. Re-logging in...")
  ```
  [login](login.md)

    END

* If the status of the HTTP response is any other and not a `2xx`:
  ```python
  logger.error(f"Got {response.status}. Response returned {response_json}")
  ```