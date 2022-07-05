## Get tickets Documentation

* if not service_number
    ```
    self._logger.info(
        f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
        f"{ticket_topic} and belonging to client {client_id} from Bruin..."
    )
    ```
* else
    ```
    self._logger.info(
        f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
        f"{ticket_topic}, service number {service_number} and belonging to client {client_id} from Bruin..."
    )
    ```
* if `Exception`
  ```
  self._logger.error(
                f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses}, "
                f"with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}"
            )
  ```
* if response_status in range(200, 300):
  * if not service_number:
    ```
    self._logger.info(
                      f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                      f"{ticket_topic} and belonging to client {client_id} from Bruin!"
                    )
    ```
  * else
    ```
    self._logger.info(
                      f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                      f"{ticket_topic}, service number {service_number} and belonging to client "
                      f"{client_id} from Bruin!"
                    )
    ```
* else
  * if not service_number
    ```
    self._logger.error(
                        f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic} and belonging to client {client_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
    ```
  * else
    ```
    self._logger.error(
                        f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic}, service number {service_number} and belonging to client {client_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
    ```
  