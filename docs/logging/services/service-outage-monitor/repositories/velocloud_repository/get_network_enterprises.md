## Get network enterprises by VCO

* If there's a filter to look for specific enterprises' networks:
  ```python
  logger.info(
      f"Getting network information for all edges belonging to enterprises "
      f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}..."
  )
  ```
* Otherwise:
  ```python
  logger.info(
      "Getting network information for all edges belonging to all enterprises in host "
      f"{velocloud_host}..."
  )
  ```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = f"An error occurred when requesting network info from Velocloud host {velocloud_host} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get networks enterprises is ok:
    * If there's a filter to look for specific enterprises' networks:
      ```python
      logger.info(
          f"Got network information for all edges belonging to enterprises "
          f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}!"
      )
      ```
    * Otherwise:
      ```python
      logger.info(
          f"Got network information for all edges belonging to all enterprises in host {velocloud_host}!"
      )
      ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while retrieving network info from Velocloud host {velocloud_host} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```