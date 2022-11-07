## Run repair tickets polling

```python
log.info("Starting RepairTicketsMonitor process...")

log.info("Getting all tagged emails...")

log.info(f"Got {len(pending_emails)} tagged emails.")

log.info(f"Got {len(repair_emails)} Repair emails: {repair_emails}")
        
log.info(f"Got {len(other_tags_emails)} emails with meaningless tags: {other_tags_emails}")
```

* for email_data in other_tags_emails
    [_process_other_tags_email](_process_other_tags_email.md)

* for email_data in repair_emails
    [_process_repair_email](_process_repair_email.md)

```python
log.info("RepairTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))
```

* if any unexpected outputs in other_tags_tasks or repair_tasks
    ```python
    log.error("Unexpected output in repair monitor coroutines: %s", output)
    ```