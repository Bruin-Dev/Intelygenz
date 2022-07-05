## Get Ticket details Documentation

```
self._logger.info(f"Getting details of ticket {ticket_id} from Bruin..."
```

* if `Exception`
  ```
  self._logger.error(f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}")
  ```

* if response_status not in range(200, 300)
  ``` 
  self._logger.error(
                    f"Error while retrieving details of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                   )
  ```
* else
  ```
  self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")
  ```
