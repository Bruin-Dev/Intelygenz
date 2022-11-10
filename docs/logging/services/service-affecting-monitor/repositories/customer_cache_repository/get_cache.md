## Get VeloCloud's customer cache

```python
logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
```

* If there's an error while asking for the data to the `customer-cache` service:
  ```python
  err_msg = f"An error occurred when requesting customer cache -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get VeloCloud's customer cache is not ok, or the cache is still building:
  ```python
  err_msg = response_body
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")
```
