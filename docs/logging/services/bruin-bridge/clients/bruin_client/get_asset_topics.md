# Get asset topics

```python
logger.info(f"Getting asset topics for: {params}")
```

Call Bruin API endpoint `GET /api/Ticket/topics` with the desired payload.

* If the status of the HTTP response is `HTTPStatus.UNAUTHORIZED`:
    ```python
    logger.error(f"Got 401 from Bruin. Re-logging in...")
    ```
    [login](../../clients/bruin_client/login.md)

    END
