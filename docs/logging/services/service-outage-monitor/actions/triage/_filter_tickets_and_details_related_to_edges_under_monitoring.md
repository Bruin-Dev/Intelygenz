## Look for ticket and tasks related to edges under monitoring

```python
logger.info(
    f"Filtering {len(tickets)} tickets and their tasks to keep only those related to edges under "
    f"monitoring..."
)
```

* For each ticket:
    ```python
    logger.info(f"Looking for relevant tasks in ticket {ticket['ticket_id']}...")
    ```

    * If the ticket has no relevant tasks:
      ```python
      logger.info(f'Ticket {ticket["ticket_id"]} has no relevant tasks. Skipping ticket...')
      ```
      _Continue with next ticket_

    ```python
    logger.info(f"Found {len(relevant_details)} relevant tasks for ticket {ticket['ticket_id']}")
    ```

```python
logger.info(f"Found {len(relevant_tickets)} tickets related to edges under monitoring")
```