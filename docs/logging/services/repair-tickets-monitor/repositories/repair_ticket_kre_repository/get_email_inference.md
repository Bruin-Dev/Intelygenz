## Get email inference

* try
    ```python
    log.info("email_id=%s Sending email data to get prediction", email_id)
    ```
    * try 
      response = event_bus.request
    * catch `Exception`
      ```python
      err_msg = f"An error occurred when sending emails to rta for email_id '{email_id}' -> {e}"
      ```
    * else
      * if response["status"] not in range 200 and 400
        ```python
        err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
        ```
      * else if response["status"] is 400
        ```python
        err_msg = (
                        f'Cannot get prediction for "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"reason {response_body}"
                    )
        ```
    * if err_msg
      ```python
      log.error(err_msg)
      ```
    * else
      ```python
      log.info("email_id=%s Prediction request sent to rta", email_id)
      ```
        
    
* Catch `Exception`
  ```python
  log.error("email_id=%s Error trying to get prediction from rta KRE %e", email_id, e)
  ```