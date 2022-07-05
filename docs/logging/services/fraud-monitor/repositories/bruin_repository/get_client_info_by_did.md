## Get client info by did
```
self._logger.info(f"Getting client info by DID {did}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when getting client info by DID {did} -> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Got client info by DID {did}!")
  ```
* Else:
  ```
  self._logger.error(f"Error while getting client info by DID {did} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}")
  ```