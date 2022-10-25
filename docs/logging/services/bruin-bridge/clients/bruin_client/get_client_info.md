# Get client info

```python
self._logger.info(f"Getting Bruin client ID for filters: {filters}")
```

Call Bruin API endpoint `GET /api/Inventory` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  self._logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
  ```
  END

* If the status of the HTTP response is `400`:
  ```python
  self._logger.error(f"Got error from Bruin {response_json}")
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  self._logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  [login](../../clients/bruin_client/login.md)

  END
