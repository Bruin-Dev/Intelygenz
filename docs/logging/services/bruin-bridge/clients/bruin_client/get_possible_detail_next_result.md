# Get possible detail next result

```python
logger.info(f"Getting work queues for ticket detail: {filters}")
```

Call Bruin API endpoint `GET /api/Ticket/{ticket_id}/nextresult` with the desired payload.

* If the status of the HTTP response is in range `200 - 299`:
  ```python
  logger.info(f"Got possible next work queue results for : {filters}")
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