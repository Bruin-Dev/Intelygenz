## Get Hawkeye's customer cache

```python
logger.info(f"Getting customer cache for Hawkeye...")
```

* If there's an error while asking for the data to the `hawkeye-customer-cache` service:
  ```python
  err_msg = f"An error occurred when requesting customer cache -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get Hawkeye's customer cache is not ok, or the cache is still building:
  ```python
  err_msg = response_body
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got customer cache for Hawkeye!")
```
