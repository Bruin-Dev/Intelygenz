# Post outage ticket

```python
logger.info(
                f"Posting outage ticket for client with ID {client_id} and for service number {service_number}"
            )

logger.info(f"Posting payload {json.dumps(payload)} to create new outage ticket...")
```

Call Bruin API endpoint `POST /api/Ticket/repair` with the desired payload.

* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"A connection error happened while trying to connect to Bruin API. Cause: {err}")
  ```
  END

* If the status of the HTTP response is in range of `200 - 300` :
  * If `errorCode` field from HTTP response is `409`
    ```python
    logger.info(
                        f"Got HTTP 409 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with In-Progress status"
                    )
    ```
  * If `errorCode` field from HTTP response is `471`
    ```python
    logger.info(
                        f"Got HTTP 471 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status"
                    )
    ```
  * If `errorCode` field from HTTP response is `472`
    ```python
    logger.info(
                        f"Got HTTP 472 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status. "
                        f"The existing ticket has been unresolved and it's now In-Progress."
                    )
    ```
  * If `errorCode` field from HTTP response is `473`
    ```python
    logger.info(
                        f"Got HTTP 473 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status for "
                        f"the same location of the service number. The existing ticket has been unresolved and it's "
                        f"now In-Progress, and a new ticket detail has been added for the specified service number."
                    )
    ```
  END

* If the status of the HTTP response is `400`:
  ```python
  logger.error(
                    f"Got HTTP 400 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    f"Reason: {response_json}"
                )
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
  logger.error(
                    "Got HTTP 403 from Bruin. Bruin client doesn't have permissions to post a new outage ticket with "
                    f"payload {json.dumps(payload)}"
                )
  ```
  END

* If the status of the HTTP response is `404`:
  ```python
  logger.error(
                    f"Got HTTP 404 from Bruin when posting outage ticket. Payload: {json.dumps(payload)}"
                )
  ```
  END

* If the status of the HTTP response is between `500` and `513` (both inclusive):
  ```python
  logger.error(
                    f"Got HTTP {status_code} from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                )
  ```
  END