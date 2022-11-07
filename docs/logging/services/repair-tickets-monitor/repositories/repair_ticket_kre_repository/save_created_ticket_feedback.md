## Save created ticket feedback

* try
    ```python
    log.info(f"Sending email and ticket data to save_created_tickets: {email_id}")
    ```
    * try 
      response = event_bus.request
    * catch `Exception`
      ```python
      err_msg = (
                    f'An error occurred when sending emails to RTA for ticket_id "{ticket_id}"'
                    f' and email_id  "{email_id}" -> {e}'
                )
      ```
    * else
      * if response["status"] not in range 200 and 300
        ```python
        err_msg = (
                        f'Error while saving created ticket feedback for email with ticket_id "{ticket_id}"'
                        f'and email_id "{email_id}" in {self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f"Error {response_status} - {response_body}"
                    )
        ```
    * if err_msg
      ```python
      log.error(err_msg)
      ```
    * else
      ```python
       log.info(f"SaveCreatedTicketFeedback request sent for email {email_id} and ticket {ticket_id} to RTA")
      ```
        
    
* Catch `Exception`
  ```python
  log.error(
                f"Error trying to save_created tickets feedback to KRE "
                f"[email_id='{email_id}', ticket_id='{ticket_id}']: {e}"
            )
  ```