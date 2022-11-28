## Get probes

```python
logger.info(f"Getting probes using filters {filters}...")
```
  
Call Hawkeye API endpoint `GET /probes` with the set of desired query parameters.

* If there's an error while connecting to Hawkeye API:

    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is `401`:

    [login](login.md)

    [__log_result](__log_result.md)

    * If max number of retries has been exceeded:
      ```python
      logger.error(f"Maximum number of retries exceeded")
      ```
      END
    * Otherwise:

        [get_probes](get_probes.md)

* If the status of the HTTP response is between `500` and `513` (both inclusive):

    [__log_result](__log_result.md)
  
    END