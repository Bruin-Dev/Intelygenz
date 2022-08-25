## Process E-mail batch

```python
logger.info(f"Processing {len(emails)} email(s) with circuit ID {circuit_id}...")
```

* If Circuit ID is undefined or Circuit ID is `SD-WAN`:
    * For each email in batch:
        * [mark email as read](../repositories/email_repository/mark_email_as_read.md)
  
    ```python
    logger.info(f"Invalid circuit_id. Skipping emails with circuit_id {circuit_id}...")
    ```
    END

[get_service_number_by_circuit_id](../repositories/bruin_repository/get_service_number_by_circuit_id.md)

* If response status for call to get inventory by circuit ID is not ok:
  ```python
  logger.error(
      f"Failed to get service number by circuit ID. Skipping emails with circuit_id {circuit_id}..."
  )
  ```
  END

  * If status = 204:
    ```python
    logger.error(
        f"Bruin returned a 204 when getting the service number for circuit_id {circuit_id}. "
        f"Marking all emails with this circuit_id as read"
    )
    ```
    * For each email in batch:
        * If environment is `PRODUCTION`:
            * [mark email as read](../repositories/email_repository/mark_email_as_read.md)
        * END

* For email in batch:
    * [_process_email](_process_email.md)

```python
logger.info(f"Finished processing all emails with circuit_id {circuit_id}!")
```