## Get VeloCloud's customer cache

* If there's a list of specific VCOs to get a cache for:
  ```python
  logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
  ```
* Otherwise:
  ```python
  logger.info(f"Getting customer cache for all Velocloud hosts...")
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
* Otherwise:
    * If there's a list of specific VCOs to get a cache for:
      ```python
      logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")
      ```
    * Otherwise:
      ```python
      logger.info(f"Got customer cache for all Velocloud hosts!")
      ```