# Post ticket notes

```python
self._logger.info(f"Getting posting notes for ticket id: {ticket_id}")

self._logger.info(f"Payload that will be applied: {json.dumps(payload)}")
```

Call Bruin API endpoint `POST /api/Ticket/{ticket_id}/notes` with the desired payload.

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
                    f"Got 404 from Bruin, resource not posted for ticket_id {ticket_id} with payload {payload}"
                )
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  self._logger.error(f"Got {response.status}.")
  ```
  END