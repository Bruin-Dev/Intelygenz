## Get existing tickets

existing_tickets = [BruinRepository:get_existing_tickets_with_service_numbers](../../repositories/bruin_repository/get_existing_tickets_with_service_numbers.md)

* if existing_tickets["status"] not 200 or 404
    Raise `ResponseException`
    ```
    "Exception while getting bruin response for existing tickets"
    ```

