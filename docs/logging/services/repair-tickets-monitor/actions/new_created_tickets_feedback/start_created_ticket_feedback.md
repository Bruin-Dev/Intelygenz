# Start created ticket feedback

```python
log.info("Scheduling New Created Tickets feedback job...")
```

* if exec_on_start:
    ```python
    log.info("NewCreatedTicketsFeedback feedback job is going to be executed immediately")
    ```

* try
    [__run_created_tickets_polling](_run_created_tickets_polling.md)

* catch `ConflictingIdError`
    ```python
    log.info(f"Skipping start of NewCreatedTicketsFeedback feedback job. Reason: {conflict}")
    ```