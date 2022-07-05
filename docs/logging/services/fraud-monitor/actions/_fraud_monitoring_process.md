## Fraud monitoring process
```
self._logger.info(f'Processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}')
```
* [get_unread_emails](../repositories/notifications_repository/get_unread_emails.md)
* If status is no Ok:
  ```
  self._logger.warning(f"Bad status calling to get unread emails. Skipping fraud monitor process")
  ```
* for email in emails:
  * If message is none or uid -1:
    ```
    self._logger.error(f"Invalid message: {email}")
    ```
  * If not email regex:
    ```
    self._logger.info(f"Email with msg_uid {msg_uid} is not a fraud warning. Skipping...")
    ```  
  * If not found body:
    ```
    self._logger.error(f"Email with msg_uid {msg_uid} has an unexpected body")
    ```  
  ```
  self._logger.info(f"Processing email with msg_uid {msg_uid}")
  ```
  * [_process_fraud](_process_fraud.md)
  * If processed and PRODUCTION:
    * If mark email as read status is Ok:
      ```
      self._logger.error(f"Could not mark email with msg_uid {msg_uid} as read")
      ```
  * If processed:
    ```
    self._logger.info(f"Processed email with msg_uid {msg_uid}")
    ```
  * Else:
    ```
    self._logger.info(f"Failed to process email with msg_uid {msg_uid}")
    ```
```
self._logger.info(
            f'Finished processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}. '
            f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
        )
```