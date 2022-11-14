## Get all open Service Outage tickets for customers under monitoring

```python
logger.info("Getting all open Service Outage tickets...")
```

[BruinRepository::get_open_outage_tickets](../../repositories/bruin_repository/get_open_outage_tickets.md)

* If response status for get open Service Outage tickets is not ok:
  ```python
  logger.error(f"Error while getting open Service Outage tickets: {open_tickets_response}")
  ```
  END

```python
logger.info(f"Got {len(open_tickets_response_body)} open Service Outage tickets")
```

```python
logger.info(
    f"Filtering open Service Outage tickets to keep only those related to customers under monitoring..."
)
```

```python
logger.info(
    f"Got {len(filtered_ticket_list)} open Service Outage tickets related to customers under monitoring"
)
```

```python
logger.info("Getting ticket tasks for each open ticket...")
```

* For each open ticket:

    [_get_open_tickets_with_details_by_ticket_id](_get_open_tickets_with_details_by_ticket_id.md)

```python
logger.info("Finished getting tickets tasks!")
```
