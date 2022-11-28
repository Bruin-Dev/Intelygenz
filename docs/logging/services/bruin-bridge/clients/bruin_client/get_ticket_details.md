# Get ticket details

```python
logger.info(f"Getting ticket details for ticket id: {ticket_id}")
```

Call Bruin API endpoint `GET /api/Ticket/{ticket_id}/details` with the desired payload.

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

* If the status of the HTTP response is `404`:
  ```python
  logger.error(f"Got 404 from Bruin, resource not found for ticket id {ticket_id}")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END