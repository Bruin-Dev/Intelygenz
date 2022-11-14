## Get sets of ticket tasks with and without a Triage note

```python
logger.info(f"Generating sets of ticket tasks with and without Triage notes based on {len(tickets)} tickets...")
```

* For each ticket:
    ```python
    logger.info(f"Checking {len(ticket_details)} tasks from ticket {ticket_id}...")
    ```

    * For each task in ticket:
        ```python
        logger.info(f"Looking for Triage notes in ticket {ticket_id} for edge {serial_number}...")
        ```

        * If there are no Triage notes for the task:
          ```python
          logger.info(f"No Triage notes found in ticket {ticket_id} for edge {serial_number}")
          ```
        * Otherwise:
          ```python
          logger.info(f"Triage notes found in ticket {ticket_id} for edge {serial_number}")
          ```

        ```python
        logger.info(f"Finished looking for Triage notes in ticket {ticket_id} for edge {serial_number}")
        ```

    ```python
    logger.info(f"Finished checking {len(ticket_details)} tasks from ticket {ticket_id}")
    ```

```python
logger.info(
    f"Generated {len(ticket_details_with_triage)} tasks with Triage notes and "
    f"{len(ticket_details_without_triage)} tasks without Triage notes"
)
```