## Filter out irrelevant notes in tickets

```python
logger.info(f"Filtering out irrelevant notes from {len(tickets)} tickets...")
```

* For each ticket:
    ```python
    logger.info(f"Filtering out irrelevant notes from ticket {ticket['ticket_id']}...")
    ```

    ```python
    logger.info(f"Got {len(relevant_notes)} relevant notes from ticket {ticket['ticket_id']}")
    ```

```python
logger.info(f"Irrelevant notes filtered out from {len(tickets)} tickets")
```