## Get network enterprises Documentation

* If enterprises ids:

  ```
  self._logger.info(
                      f"Getting network information for all edges belonging to enterprises "
                      f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}..."
                  )
  ```
* Else:

  ```
  self._logger.info(
                      "Getting network information for all edges belonging to all enterprises in host "
                      f"{velocloud_host}..."
                  )
  ```


* If `Exception`

  ```
  self._logger.error(f"An error occurred when requesting network info from Velocloud host {velocloud_host} -> {e}")
  ```
* If status OK:

  * If enterprises ids:

    ```
    self._logger.info(
                            f"Got network information for all edges belonging to enterprises "
                            f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}!"
                        )
    ```
  * Else:

    ```
    self._logger.info(
                            f"Got network information for all edges belonging to all enterprises in host {velocloud_host}!"
                        )
    ```


* Else:

  ```
  self._logger.error(f"Error while retrieving network info from Velocloud host {velocloud_host} in "
                      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}")
  ```
