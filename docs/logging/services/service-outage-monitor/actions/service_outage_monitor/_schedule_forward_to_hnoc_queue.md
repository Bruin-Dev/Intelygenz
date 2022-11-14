## Schedule forward to HNOC for ticket task

```python
logger.info(
    f"Scheduling forward to {target_queue.value} for ticket {ticket_id} and serial number {serial_number} "
    f"to happen in {forward_time} minutes"
)
```

_Forward to HNOC for ticket task is scheduled to happen after some time if it's a Link Down outage, or immediately otherwise_