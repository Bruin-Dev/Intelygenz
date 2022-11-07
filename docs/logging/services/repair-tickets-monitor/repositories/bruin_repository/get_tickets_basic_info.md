## Get tickets basic info

* try
  * try
    ```python
    log.info(
                    f"Getting all tickets with any status of {ticket_statuses},with keyword arguments {kwargs}"
                )
    ```
    response = event_bus.request

    * catch `Exception`
        ```python
        err_msg = (
                    f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses} "
                    f"with keyword arguments {kwargs} -> {e}"
                )
        ```
    * else
      * if response["status"] in range of 200 and 300
          ```python
          log.info(
                        f"Got all tickets with any status of {ticket_statuses}, with ticket _topic "
                        f"and keyword arguments {kwargs} from Bruin!"
                    )
          ```
      * else 
        ```python
        err_msg = (
                    f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses} "
                    f"with keyword arguments {kwargs} -> {e}"
                )
        ```
    * if err_msg
        ```python
        log.error(err_msg)
        ```
* catch `Exception`
    ```python
    log.error(f"Error getting tickets with keyword arguments {kwargs} from Bruin: {e}")
    ```