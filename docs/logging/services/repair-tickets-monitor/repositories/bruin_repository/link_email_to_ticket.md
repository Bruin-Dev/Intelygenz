## Link email to ticket

* try
    response = event_bus.request

* except 'Exception'
    ```python
    error_message = (f"email_id={email_id} An error occurred linking ticket {ticket_id}\n Error: {e}",)
    ```

* if response["status"] not 200
    ```python
    log.error( f"email_id={email_id} Error response from bruin-bridge while linking the {ticket_id}"
                f"{self._config.ENVIRONMENT_NAME.upper()} environment."
                f"{response['status']} - {response['body']}"
            )
    ```

```python
log.info("email_id=%s, linked to ticket %s", email_id, ticket_id)
```