## Append notes to ticket


* try
   response = event_bus.request
* catch `Exception`
    ```python
    log.error(
                f"ticket_id={ticket_id} An error occurred during RPC communication\n"
                f"Request sent: {rpc_request}\n"
                f"Error: {e}"
            )
    ```
* if response["status"] not 200
  ```python
  log.error(
                f"ticket_id={ticket_id} Bruin returned a not success status\n"
                f"Request: {rpc_request}\n"
                f"Response: {response['status']} - {response['body']}"
            )
  ```


```python
log.info("ticket_id=%s Note appended to ticket successfully!\n Note published: %s", ticket_id, response["body"])
```
