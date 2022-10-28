# Change detail work queue 

```python
logger.info(f"Changing work queue for ticket detail: {filters} and ticket id : {ticket_id}")
```

Call Bruin API endpoint `PUT /api/Ticket/{ticket_id}/details/work` with the desired payload.

* If the status of the HTTP response is in range `200 - 299`:
  ```python
  logger.info(f"Work queue changed for ticket detail: {filters}")
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

* If the status of the HTTP response is in range `500 - 513`:
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END