## Make an HTTP request to ServiceNow API

Make a call to the desired API endpoint with the specified payload or query parameters.

* If there's an error while making the call to the ServiceNow API:
  ```python
  log.exception(e)
  ```
  END

* If the status of the HTTP response is `401`:
    ```python
    log.error(f"Got 401 from Bruin. Re-logging in...")
    ```
    [_get_access_token](_get_access_token.md)

    Retry same exact HTTP call.