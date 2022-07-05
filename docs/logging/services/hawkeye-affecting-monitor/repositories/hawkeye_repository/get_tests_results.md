## Get tests results
## Get probes
```
self._logger.info(f"Getting tests results for {len(probe_uids)} probes from Hawkeye...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting tests results from Hawkeye -> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Error while retrieving tests results: Error {response_status} - {response_body}")
  ```
* Else:
  ```
  self._logger.error(f"Got all tests results for {len(probe_uids)} probes from Hawkeye!")
  ```