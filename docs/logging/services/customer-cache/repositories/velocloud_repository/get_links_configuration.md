## Get links' configuration for an edge

```python
logger.info(f"Getting links configuration for edge {edge}...")
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = f"An error occurred when requesting links configuration for edge {edge} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get links' configuration for the edge is not ok:
  ```python
  err_msg = (
      f"Error while retrieving links configuration for edge {edge} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got links configuration for edge {edge}!")
```