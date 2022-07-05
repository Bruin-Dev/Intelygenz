## Get ticket basic info
```
self._logger.info(
                f"Getting all tickets basic info with any status of {ticket_statuses}, with ticket topic "
                f"VOO, service number {service_number} and belonging to client {client_id} from Bruin..."
            )
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting tickets  basic info from Bruin API with any status"
                f" of {ticket_statuses}, with ticket topic VOO and belonging to client {client_id} -> {e}")
  ```
* If status not Ok:
  ```
  self._logger.error(f"Error while retrieving tickets basic info with any status of {ticket_statuses}, "
                    f"with ticket topic VOO, service number {service_number} and belonging to client {client_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```
* Else:
  ```
  self._logger.info(
                    f"Got all tickets basic info with any status of {ticket_statuses}, with ticket topic "
                    f"VOO, service number {service_number} and belonging to client "
                    f"{client_id} from Bruin!"
                )
  ```