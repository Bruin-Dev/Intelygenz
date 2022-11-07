## Get site


* try
   ```python
   log.info(f"Getting site for site_id {site_id} of client {client_id}...")
   ```
   response = event_bus.request
* catch `Exception`
    ```python
    err_msg = f"An error occurred while getting site for site_id {site_id} Error: {e} "
    ```
* else 
    * if response["status"] in range 200 and 300
        ```python
        log.info(f"Got site details of site {site_id} and client {client_id} successfully!")
        ```
    * else
        ```python
        err_msg = (
                f"An error response from bruin while getting site information for site_id {site_id} "
                f"{self._config.ENVIRONMENT_NAME.upper()} environment."
                f"Error {response_status} - {response_body}"
            )
        ```
* if err_msg
    ```python
    log.error(err_msg)
    ```
