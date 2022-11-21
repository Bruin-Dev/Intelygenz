## Get enterprise events

```
self._logger.info(
                f"Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} "
                f"that took place between {past_moment} and {now} from Velocloud..."
            )
```

* If `Exception`

  ```
  self._logger.error(f"An error occurred when requesting edge events from Velocloud for host {host} "
                f"and enterprise id {enterprise_id} -> {e}")
  ```

* If status is Ok:
  ```
  self._logger.info(
                    f"Got events of host {host} and enterprise id {enterprise_id} having any type in {event_types} "
                    f"that took place between {past_moment} and {now} from Velocloud!"
                )
  ```

* Else:

  ```
  self._logger.error(f"Error while retrieving events of host {host} and enterprise id {enterprise_id} having any type "
                    f"in {event_types} that took place between {past_moment} and {now} "
                    f"in {self._config.ENVIRONMENT_NAME.upper()}"
                    f"environment: Error {response_status} - {response_body}")
  ```