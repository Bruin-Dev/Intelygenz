## Get all events

* If there's no cookie for the VeloCloud host:
    ```python
    logger.error(f"Cannot find a cookie for {host}")
    ```

    [_login](_login.md)

    END

```python
logger.info(f"Getting all events from host {host} using payload {body}...")
```
  
Call VeloCloud API endpoint `POST /event/getEnterpriseEvents` with the set of desired parameters.

* If the status of the HTTP response is `200`:
  ```python
  logger.info(f"Got HTTP 200 from POST /event/getEnterpriseEvents for host {host} and payload {body}")
  ```
  END

* If the status of the HTTP response is `400`:
  ```python
  logger.error(f"Got HTTP 400 from Velocloud: {response_json}")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got HTTP {response.status} from Velocloud")
  ```
  END