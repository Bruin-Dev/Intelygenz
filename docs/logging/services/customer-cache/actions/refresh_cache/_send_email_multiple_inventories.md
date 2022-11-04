## Send an e-mail with a summary of all edges having multiple inventories in Bruin

* If there are edges with multiple inventories in Bruin:
    ```python
    message = f"Alert. Detected some edges with more than one status. {self._serials_with_multiple_inventories}"
    [...]
    logger.warning(message)
    ```

    ```python
    logger.info(
        f"Sending mail with serials having multiples inventories to  "
        f"{email_obj['body']['email_data']['recipient']}"
    )
    ```
    _E-mail is sent_
    ```python
    logger.info(f"Response from sending email with serials having multiple inventories: {json.dumps(response)}")
    ```

* Otherwise:
  ```python
  logger.info("No edges with multiple Bruin inventories were detected")
  ```