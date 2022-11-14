## Process ticket tasks with Triage / Events notes

```python
logger.info(f"Processing {len(ticket_details)} ticket tasks with Triage / Events notes...")
```

* For each task:
    ```python
    logger.info(f"Processing task with Triage / Events note of ticket {ticket_id} for edge {serial_number}...")
    ```

    ```python
    logger.info(
        f"Checking if Events note needs to be appended to task of ticket {ticket_id} "
        f"for edge {serial_number}..."
    )
    ```

    * If the last Triage / Events note was appended too recently:
      ```python
      logger.info(
          f"The last Triage / Events note was appended to task of ticket {ticket_id} for edge "
          f"{serial_number} not long ago so no new Events note will be appended for now"
      )
      ```
      _Continue with next task_

    ```python
    logger.info(f"Appending Events note to task of ticket {ticket_id} for edge {serial_number}...")
    ```

    [_append_new_triage_notes_based_on_recent_events](_append_new_triage_notes_based_on_recent_events.md)

    ```python
    logger.info(f"Events note appended to task of ticket {ticket_id} for edge {serial_number}!")
    ```

    ```python
    logger.info(f"Finished processing task of ticket {ticket_id} for edge {serial_number}!")
    ```

```python
logger.info(f"Finished processing {len(ticket_details)} ticket tasks with Triage / Events notes!")
```