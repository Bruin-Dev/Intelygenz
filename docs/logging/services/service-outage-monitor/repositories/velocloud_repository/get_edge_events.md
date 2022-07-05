## Get edge events
```
self._logger.info(f"Getting events of edge {json.dumps(edge_full_id)} having any type of {event_types} that took place "
                f"between {from_} and {to} from Velocloud...")
```
* If Exception:
  ```
        self._logger.error(f"An error occurred when requesting edge events from Velocloud for edge "
                f"{json.dumps(edge_full_id)} -> {e}")
  ```
```
      self._logger.info(f"Got events of edge {json.dumps(edge_full_id)} having any type in {event_types} that took place "
                f"between {from_} and {to} from Velocloud!")
```
* If status not ok:
```
        self._logger.error(f"Error while retrieving events of edge {json.dumps(edge_full_id)} having any type in "
                    f"{event_types} that took place between {from_} and {to} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}")
```