## Mark email as done


* try
   ```python
   log.info(f"Marking email {email_id} as done...")
   ```
   response = event_bus.request
* catch `Exception`
    ```python
    err_msg = f"An error occurred while marking email {email_id} as done. {e}"
    ```
* else 
    * if response["status"] in range 200 and 300
        ```python
        log.info(f"Marked email {email_id} as done successfully!")
        ```
    * else
        ```python
        err_msg = (
                    f"An error occurred while marking {email_id} as done in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error {response_status} - {response_body}"
                )
        ```
* if err_msg
    ```python
    log.error(err_msg)
    ```
