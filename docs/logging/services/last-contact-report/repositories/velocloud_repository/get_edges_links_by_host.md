## Get links with edge info by VCO

```python
logger.info(f"Getting edges links from Velocloud for host {host}...")
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = f"An error occurred when requesting edge list from {host} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info("Got edges links from Velocloud!")
```

* If response status for get links with edge info is not ok:
  ```python
  err_msg = (
      f"Error while retrieving edges links in {self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
