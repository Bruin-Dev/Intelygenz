## Schedule forward to queue

```python
self._logger.info(
    f"Scheduling {target_queue} queue forwarding for ticket_id {ticket_id} and service number {serial_number}"
    f" to happen at timestamp: {forward_task_run_date}"
)
```

[forward_ticket_to_queue](forward_ticket_to_queue.md)