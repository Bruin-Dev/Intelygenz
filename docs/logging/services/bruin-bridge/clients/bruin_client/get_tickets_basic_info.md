## Get tickets basic info

```python
self._logger.info(f"Getting tickets basic info using params {json.dumps(request_params)}...")
```
  
Call Bruin API endpoint `GET /api/Ticket/basic` with the set of desired query parameters.

* If there's an error while connecting to Bruin API:
  ```python
  self._logger.error(f"A connection error happened while trying to connect to Bruin API: {e}")
  ```
  END

* If the status of the HTTP response is `200`:
  ```python
  self._logger.info(f"Got HTTP 200 from GET /api/Ticket/basic for params {json.dumps(request_params)}")
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

* If the status of the HTTP response is `403`:
  ```python
  self._logger.error(f"Forbidden error from Bruin {response_json}")
  ```
  END

* If the status of the HTTP response is `404`:
  ```python
  self._logger.error(f"Got 404 from Bruin, resource not found for params {request_params}")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  self._logger.error(f"Got {response.status}.")
  ```
  END