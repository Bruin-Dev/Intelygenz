# Unpause ticket

```python
self._logger.info(f"Unpause ticket for ticket id: {ticket_id} with filters {filters}")
```

Call Bruin API endpoint `POST /api/Ticket/{ticket_id}/detail/unpause` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  self._logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
  ```
  END

* If the status of the HTTP response is in range `200 - 300`:
  ```python
  self._logger.info(f"Correct unpause ticket for ticket id: {ticket_id} with filters {filters}")
  ```
  END
 
* If the status of the HTTP response is `400`:
  ```python
  self._logger.error(f"Got error 400 from Bruin {response_json}")
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  self._logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  [login](../../clients/bruin_client/login.md)

  END

* If the status of the HTTP response is `403`:
  ```python
  self._logger.error(f"Forbidden error from Bruin {response_json}")
  ```
  END
 
* If the status of the HTTP response is in range `500 - 513`:
  ```python
  self._logger.error(f"Got {response.status}.")
  ```
  END