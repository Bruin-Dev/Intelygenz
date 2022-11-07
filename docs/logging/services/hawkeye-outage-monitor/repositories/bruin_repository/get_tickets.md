## Get tickets

* If no service number was specified:
  ```python
  logger.info(
      f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
      f"{ticket_topic} and belonging to client {client_id} from Bruin..."
  )
  ```
* Otherwise:
  ```python
  logger.info(
      f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
      f"{ticket_topic}, service number {service_number} and belonging to client {client_id} from Bruin..."
  )
  ```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses}, "
      f"with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get tickets is not ok:
    * If no service number was specified:
      ```python
      err_msg = (
          f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
          f"{ticket_topic} and belonging to client {client_id} in "
          f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
          f"Error {response_status} - {response_body}"
      )
      [...]
      logger.error(err_msg)
      ```
    * Otherwise:
      ```python
      err_msg = (
          f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
          f"{ticket_topic}, service number {service_number} and belonging to client {client_id} in "
          f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
          f"Error {response_status} - {response_body}"
      )
      [...]
      logger.error(err_msg)
      ```

    END

* If no service number was specified:
  ```python
  logger.info(
      f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
      f"{ticket_topic} and belonging to client {client_id} from Bruin!"
  )
  ```
* Otherwise:
  ```python
  logger.info(
      f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
      f"{ticket_topic}, service number {service_number} and belonging to client "
      f"{client_id} from Bruin!"
  )
  ```