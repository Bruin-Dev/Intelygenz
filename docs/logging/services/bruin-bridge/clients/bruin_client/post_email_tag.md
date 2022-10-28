# Post email tag

* try
```python
logger.info(f"Sending request to /api/Email/{email_id}/tag/{tag_id}")
```

Call Bruin API endpoint `POST /api/Email/{email_id}/tag/{tag_id}` with the desired payload.

```python
logger.info(f"Got response from Bruin. Status: {response.status} Response: {response}.")
```

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

  * If the status of the HTTP response is `403`:
    ```python
    logger.error(f"Forbidden error from Bruin {response_json}")
    ```
    END

  * If the status of the HTTP response is `404`:
    ```python
    logger.error(
                      f"Got 404 from Bruin, resource not posted for email_id {email_id} with tag_id {tag_id}"
                  )
    ```
    END

  * If the status of the HTTP response is `409`:
    ```python
    logger.error(
                      f"Got 409 from Bruin, resource not posted for email_id {email_id} with tag_id {tag_id}"
                  )
    ```
    END
  * 
  * If the status of the HTTP response is in range `500 - 513`:
    ```python
    logger.error(f"Got {response.status}.")
    ```
    END
* catch `Exception`
  ```python
  logger.error(f"Exception during call to post_email_tag. Error: {e}.")
  ```