## Verify service number information

* try
    ```python
    log.info(f'Getting inventory "{client_id}" and service number {service_number}')
    ```
    * try 
      response = event_bus.request
    
    * catch `Exception`
        ```python
        err_msg = (
                    f"An error occurred when getting service number info from Bruin, "
                    f'for ticket_id "{client_id}" -> {err}'
                )
        ```
    * else
        * if response["status"] not in range 200 and 300
            ```python
            err_msg = (
                        f"Error getting service number info for {service_number} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
            ```
        * else if no response["body"]
            ```python
            log.info(f"Service number not validated {service_number}")
            ```
    
    * if err_msg
        ```python
        log.error(err_msg)
        ```
    * else
        ```python
        log.info(f"Service number info {service_number} retrieved from Bruin")
        ```

* catch `Exception`
    ```python
    log.error(f"Error getting service number info {service_number} from Bruin: {e}")
    ```