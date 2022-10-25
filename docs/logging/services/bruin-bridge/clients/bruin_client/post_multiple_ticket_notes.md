# Post multiple ticket notes

```python
self._logger.info(f"Posting multiple notes for ticket id: {ticket_id}. Payload {json.dumps(payload)}")
```

Call Bruin API endpoint `POST /api/Ticket/{ticket_id}/notes/advanced` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  self._logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
  ```
  END

* If the status of the HTTP response is `400`:
  ```python
  self._logger.error(f"Got error from Bruin {response_json}")
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

* If the status of the HTTP response is `404`:
  ```python
  self._logger.error(
                    f"Got 404 from Bruin, resources not posted for ticket_id {ticket_id} with payload {payload}"
                )
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  self._logger.error(f"Got {response.status}.")
  ```
  END