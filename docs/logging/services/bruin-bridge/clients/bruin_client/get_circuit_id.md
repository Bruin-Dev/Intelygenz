# Get circuit id

```python
logger.info(f"Getting the circuit id from bruin with params {parsed_params}")
```

Call Bruin API endpoint `GET /api/Inventory/circuit` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
  ```
  END

* If the status of the HTTP response is in range `200 - 300`:
  ```python
  logger.info(f"Got circuit id from bruin with params: {parsed_params}")
  ```
  END
 
* If the status of the HTTP response is `204`:
  ```python
  logger.error("Got status 204 from Bruin")
  ```
  END

* If the status of the HTTP response is `400`:
  ```python
  logger.error(f"Got error 400 from Bruin {response_json}")
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  [login](../../clients/bruin_client/login.md)

  END

* If the status of the HTTP response is `403`:
  ```python
  logger.error(f"Forbidden error from Bruin {response_json}")
  ```
  END
 
* If the status of the HTTP response is in range `500 - 513`:
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END