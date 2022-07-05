## Get attributes serial
```
self._logger.info(f"Getting the attribute's serial number of serial number {service_number}")
```
* If Exception:
  ```
  self._logger.error(f"Getting the attribute's serial number of serial number {service_number} Error: {e}")
  ```
* If status not Ok:
  ```
  self._logger.error(f"'Getting the attribute's serial number of serial number {service_number}'"
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
                    f"Error {response_status} - {response_body}")
  ```
* Else:
  ```
  self._logger.info(f"Got the attribute's serial number of serial number {service_number}!")
  ```