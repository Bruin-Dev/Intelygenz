# Get ticket task history

```python
logger.info(f"Getting ticket task history for ticket: {filters}")
```

Call Bruin API endpoint `GET /api/Ticket/AITicketData?ticketId={ticketId}` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
  ```
  END

* If the status of the HTTP response is in range `200 - 300`:
  ```python
  logger.info(f"Got ticket task history for : {filters}")
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

* If the status of the HTTP response is in range `500 - 513`:
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END