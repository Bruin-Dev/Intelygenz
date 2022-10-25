# Update ticket status

```python
self._logger.info(f"Updating ticket status for ticket id: {ticket_id}")

self._logger.info(f"Payload that will be applied (parsed to PascalCase): {json.dumps(payload)}")
```

Call Bruin API endpoint `PUT /api/Ticket/{ticket_id}/details/{detail_id}/status` with the desired payload.

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
  self._logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
  ```
  END

* If the status of the HTTP response is between `500` and `512` (both inclusive):
  ```python
  self._logger.error(f"Got {response.status}.")
  ```
  END