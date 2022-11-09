## Get existing tickets with service numbers

```python
log.info(
            "Getting tickets for client %s with status %s for site_ids %s with topics %s",
            client_id,
            ticket_statuses,
            site_ids,
            ticket_topic,
        )
```

* for site_id in site_ids
    [get_tickets_basic_info](get_tickets_basic_info.md)

* for ticket in tickets
    details = [get_ticket_details](get_ticket_details.md)
    * if details["status"] is not 200
        ```python
        log.error(f"Error while retrieving details from ticket {ticket_id}")
        ```