# Get client info by did

```python
 logger.info(f"Getting Bruin client info by DID: {did}")
```

Call Bruin API endpoint `GET /api/Inventory/phoneNumber/Lines` with the desired payload.

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
