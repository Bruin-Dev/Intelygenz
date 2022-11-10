## Schedule forward to HNOC queue for ticket task

```python
logger.info(
    f"Scheduling forward to {target_queue.value} for ticket {ticket_id} and serial number {serial_number} "
    f"to happen in {forward_time} minutes"
)
```

_Forward to HNOC is scheduled to happen after some time_