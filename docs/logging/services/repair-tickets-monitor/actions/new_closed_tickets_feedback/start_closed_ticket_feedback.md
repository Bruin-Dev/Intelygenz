# Start closed ticket feedback

```python
log.info("Scheduling New Closed Tickets feedback job...")
```

* if exec_on_start:
    ```python
    log.info("NewClosedTicketsFeedback feedback job is going to be executed immediately")
    ```

* try
    [_run_closed_tickets_polling](_run_closed_tickets_polling.md)

* catch `ConflictingIdError`
    ```python
    log.info(f"Skipping start of NewClosedTicketsFeedback feedback job. Reason: {conflict}")
    ```