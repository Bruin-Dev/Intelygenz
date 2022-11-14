## Get links with edge info by VCO

```python
logger.info(f"Getting links with edge info from Velocloud for host {velocloud_host}...")
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = f"An error occurred when requesting edge list from Velocloud -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get links with edge info is ok:
  ```python
  logger.info(f"Got links with edge info from Velocloud for host {velocloud_host}!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while retrieving links with edge info in {self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```