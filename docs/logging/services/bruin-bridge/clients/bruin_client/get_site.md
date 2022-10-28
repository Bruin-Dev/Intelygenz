## Get site

```python
logger.info(f"Getting Bruin Site for params: {params}")
```
  
Call Bruin API endpoint `GET /api/Site` with the set of desired query parameters.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
  ```
  END

* If the status of the HTTP response is `200`:
  ```python
  logger.info(f"Got HTTP 200 from GET /api/Site for params {json.dumps(params)}")
  ```
  END

* If the status of the HTTP response is `400`:
  ```python
  logger.error(f"Got error from Bruin {response_json}")
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
  logger.error(f"Got HTTP 403 from Bruin")
  ```
  END

* If the status of the HTTP response is `404`:
  ```python
  logger.error(f"Got HTTP 404 from Bruin")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got HTTP {response.status} from Bruin")
  ```
  END