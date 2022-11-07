# Get closed tickets created during last 3 days

response = [BruinRepository:get_closed_tickets_with_creation_date_limit](../../repositories/bruin_repository/get_closed_tickets_with_creation_date_limit.md)

* if response["status"] not in range of 200 and 300:
    ```python
    log.error("Error while getting bruin closed tickets")
    ```
