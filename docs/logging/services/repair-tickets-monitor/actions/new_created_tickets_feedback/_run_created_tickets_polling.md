## Run created tickets polling

```python
log.info("Starting NewCreatedTicketsFeedback feedback process...")

log.info("Getting all new tickets...")

log.info(f"Got {len(new_tickets)} tickets that needs processing.")
```

* for data in new_tickets
  [_save_created_ticket_feedback](_save_created_ticket_feedback.md)

```python
log.info(f"print output {output}")

log.info("NewCreatedTicketsFeedback process finished! Took {:.3f}s".format(time.time() - start_time))
```