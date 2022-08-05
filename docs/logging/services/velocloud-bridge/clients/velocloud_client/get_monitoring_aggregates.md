## Get monitoring aggregates

```python
logger.info(f"Getting monitoring aggregates for host {client['host']}")
```

Call VeloCloud API endpoint `POST /monitoring/getAggregates`.

* If the status of the HTTP response is `200`:
    ```python
    logger.info(f"Got HTTP 200 from POST /monitoring/getAggregates for host {client['host']}")
    ```

    [_json_return](_json_return.md)

    END

* If the status of the HTTP response is `400`:
  ```python
  logger.error(f"Got HTTP 400 from Velocloud {response_json}")
  ```

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got HTTP {response.status}")
  ```
