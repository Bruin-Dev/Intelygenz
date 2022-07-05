## Get enterprise events Documentation

```
self._logger.info(
                f"Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} "
                f"that took place between {past_moment} and {now} from Velocloud..."
            )
```

* if `Exception`:
  ```
  self._logger.error(
                f"An error occurred when requesting edge events from Velocloud for host {host} "
                f"and enterprise id {enterprise_id} -> {e}"
            )
  ```
* if response_status in range(200, 300)
  ```
  self._logger.info(
                    f"Got events of host {host} and enterprise id {enterprise_id} having any type in {event_types} "
                    f"that took place between {past_moment} and {now} from Velocloud!"
                )
  ```
* else
  ```
  self._logger.error(
                    f"Error while retrieving events of host {host} and enterprise id {enterprise_id} having any type "
                    f"in {event_types} that took place between {past_moment} and {now} "
                    f"in {self._config.ENVIRONMENT_NAME.upper()}"
                    f"environment: Error {response_status} - {response_body}"
                )
  ```