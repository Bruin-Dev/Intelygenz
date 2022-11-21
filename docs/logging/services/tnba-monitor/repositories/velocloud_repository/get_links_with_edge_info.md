## Get Links with edge info Documentation

```
self._logger.info(f"Getting links with edge info from Velocloud for host {velocloud_host}...")
```

* If `Exception`

  ```
  self._logger.error(f"An error occurred when requesting edge list from Velocloud -> {e}")
  ```
* If status OK:

  ```
  self._logger.info(f"Got links with edge info from Velocloud for host {velocloud_host}!")
  ```
* Else:

  ```
  self._logger.error(f"Error while retrieving links with edge info in {self._config.ENVIRONMENT_NAME.upper()} "
                      f"environment: Error {response_status} - {response_body}")
  ```
