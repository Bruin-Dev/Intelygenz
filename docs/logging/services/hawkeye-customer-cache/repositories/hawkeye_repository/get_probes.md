## Get all probes from Ixia

```python
logger.info(f"Getting all probes from Hawkeye...")
```

* If there's an error while asking for the data to the `hawkeye-bridge`:
  ```python
  err_msg = f"An error occurred when requesting all probes from Hawkeye -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get probes is not ok:
  ```python
  err_msg = f"Error while retrieving probes: Error {response_status} - {response_body}"
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info("Got all probes from Hawkeye!")
```