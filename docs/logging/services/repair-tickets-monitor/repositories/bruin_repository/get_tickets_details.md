## Get ticket details

* try
    * try
       ```python
       log.info(f"Getting details of ticket {ticket_id} from Bruin...")
       ```
       response = event_bus.request
    * catch `Exception`
        ```python
        err_msg = (
                    f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}"
                )
        ```
    * else 
        * if response["status"] not in range 200 and 300
            ```python
            err_msg = (
                        f"Error while retrieving details of ticket {ticket_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
            ```
        * else
            ```python
            log.info(f"Got details of ticket {ticket_id} from Bruin!")
            ```
    * if err_msg
        ```python
        log.error(err_msg)
        ```
* catch `Exception`
    ```python
    log.error(f"Error getting ticket details for {ticket_id} from Bruin: {e}")
    ```