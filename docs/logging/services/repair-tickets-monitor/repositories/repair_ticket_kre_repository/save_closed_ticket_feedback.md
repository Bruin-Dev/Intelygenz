## Save closed ticket feedback

* try
    ```python
    log.info("ticket_id=%s Sending ticket data to save_closed_tickets", ticket_id)
    ```
    * try 
      response = event_bus.request
    * catch `Exception`
      ```python
      err_msg = f'An error occurred when sending tickets to RTA for ticket_id "{ticket_id} {e}"'
      ```
    * else
      * if response["status"] not in range 200 and 300
        ```python
        err_msg = (
                        f'Error while saving closed ticket feedback for with ticket_id "{ticket_id}"'
                        f"in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
        ```
    * if err_msg
      ```python
      log.error(err_msg)
      ```
    * else
      ```python
      log.info("ticket_id=%s Save closed request sent to RTA", ticket_id)
      ```
        
    
* Catch `Exception`
  ```python
  log.error(f"Error trying to save closed tickets feedback to KRE [ticket_id='{ticket_id}']: {e}")
  ```