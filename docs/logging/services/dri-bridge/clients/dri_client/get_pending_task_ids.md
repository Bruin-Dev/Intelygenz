## Get pending tasks for serial number

```python
logger.info(f"Getting list of pending task ids for serial number {serial_number}...")
```

Make a call to `GET /acs/device/{serial_number}/taskpending`.

* If there's an error while connecting to DRI API:
  ```python
  logger.error(f"An error occurred while getting list of pending task ids for serial number {serial_number}")
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