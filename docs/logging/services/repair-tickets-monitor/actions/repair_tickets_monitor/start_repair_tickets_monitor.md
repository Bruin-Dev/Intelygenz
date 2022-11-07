## Start repair tickets monitor

```python
log.info("Scheduling RepairTicketsMonitor job...")
```

* if exec_on_start
    ```python
    log.info("RepairTicketsMonitor job is going to be executed immediately")
    ```

* try
    [_run_repair_tickets_polling](_run_repair_tickets_polling.md)

* catch `ConflictingIdError`
    ```python
    log.info(f"Skipping start of repair tickets monitor job. Reason: {conflict}")
    ```
