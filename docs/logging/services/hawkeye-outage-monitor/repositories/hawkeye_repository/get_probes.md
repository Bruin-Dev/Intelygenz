## Get probes
```
self._logger.info(f"Getting all probes from Hawkeye...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting all probes from Hawkeye -> {e}")
  ```
* If status ok:
  ```
  self._logger.info("Got all probes from Hawkeye!")
  ```
* Else:
  ```
  self._logger.error(f"Error while retrieving probes: Error {response_status} - {response_body}")
  ```