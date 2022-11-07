## Run closed tickets polling

```python
log.info("Starting NewClosedTicketsFeedback feedback process...")
```

[get_closed_tickets_created_during_last_3_days](get_closed_tickets_created_during_last_3_days.md)

```python
log.info(f"Got igz closed tickets: {len(igz_tickets)}")
```

* for ticket in igz_tickets
    [_save_closed_ticket_feedback](_save_closed_ticket_feedback.md)