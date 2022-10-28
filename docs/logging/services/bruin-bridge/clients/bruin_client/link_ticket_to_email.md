# Link ticket to email

```python
logger.info(f"Linking ticket {ticket_id} with email {email_id}")
```

Call Bruin API endpoint `POST /api/Email/{email_id}/link/ticket/{ticket_id}` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
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
  logger.error(f"Got HTTP {response.status} from Bruin")
  ```
  END