# Post notification email milestone

```python
logger.info(
    f'Sending milestone email for ticket id {payload["ticket_id"]}, service number'
    f' {payload["detail"]["service_number"]} and notification type'
    f' {payload["notification_type"]}'
)

logger.info(f"Payload that will be applied : {json.dumps(payload, indent=2)}")
```

Call Bruin API endpoint `POST /api/Notification/email/milestone` with the desired payload.

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
  logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
  ```
  END

* If the status of the HTTP response is in range `500 - 513`:
  ```python
  logger.error(f"Got {response.status}.")
  ```
  END