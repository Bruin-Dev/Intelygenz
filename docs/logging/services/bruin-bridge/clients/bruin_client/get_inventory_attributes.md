# Get inventory attributes

```python
logger.info(f'Getting inventory_attributes for client ID: {filters["client_id"]}')

logger.info(f"Filters that will be applied (parsed to PascalCase): {json.dumps(parsed_filters)}")
```

Call Bruin API endpoint `GET /api/Inventory/Attribute` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
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
  logger.error(f"Forbidden error from Bruin {response_json}")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END