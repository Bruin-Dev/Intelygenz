## get cache Documentation

1. If velo_filter

   ```
   self._logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
   ```
2. Else:

   ```
   self._logger.info(f"Getting customer cache for all Velocloud hosts...")
   ```
3. If `Exception`:

   ```
   self._logger.error(f"An error occurred when requesting customer cache -> {e}")
   ```

* If response status == 202:
  ```
  self._logger.error(response_body)
  ```
* Else:
  * If velo_filter:

    ```
    self._logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")
    ```
  * Else

    ```
    self._logger.info(f"Got customer cache for all Velocloud hosts!")
    ```
