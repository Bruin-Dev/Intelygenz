## Save created ticket feedback

response = [BruinRepository:get_single_ticket_info_with_service_numbers](../../repositories/bruin_repository/get_single_ticket_info_with_service_numbers.md)

* if response['status'] not in range of 200 and 300:
  [_check_error](_check_error.md)

```python
log.info(f"Got ticket info from Bruin: {ticket_response}")
```

site_map = [_get_site_map_for_ticket](_get_site_map_for_ticket.md)

* if no site_map
    ```python
    log.error(f"Could not create a site map for ticket {ticket_id}")
    ```

[RepairTicketKreRepository:save_created_ticket_feedback](../../repositories/repair_ticket_kre_repository/save_created_ticket_feedback.md)

```python
log.info(f"Got response from kre {response}")
```

[NewCreatedTicketsRepository:mark_complete](../../repositories/new_created_tickets_repository/mark_complete.md)]