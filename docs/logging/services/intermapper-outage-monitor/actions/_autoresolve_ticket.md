## Autoresolve ticket

```python
logger.info("Starting the autoresolve process")
```
  
[get_ticket_basic_info](../repositories/bruin_repository/get_ticket_basic_info.md)

* If response status for get tickets basic info is not ok:
  ```python
  logger.warning(
      f"Bad status calling to get ticket basic info for client id:  {client_id}."
      f"Skipping autoresolve ticket ..."
  )
  ```
  END

```python
logger.info(
    f"Found {len(tickets_body)} tickets for service number {service_number} from bruin: {tickets_body}"
)
```

* For ticket in tickets:
    * If current condition has already been reported on the ticket:
      ```python
      logger.info(
          f"Current condition has already been reported on ticket id {ticket_id}. "
          f"Skipping append note to ticket..."
      )
      ```
    * Else:
        ```python
        logger.info(
            f"Posting InterMapper UP note to task of ticket id {ticket_id} "
            f"related to service number {service_number}..."
        )
        ```
        
        [_append_intermapper_up_note](../repositories/bruin_repository/append_intermapper_up_note.md)
        
        * If response status for append InterMapper UP note is not ok:
          ```python
          logger.warning(
              f"Bad status calling to append intermapper note to ticket id: {ticket_id}."
              f"Skipping autoresolve ticket ...."
          )
          ```
          END

    [get_tickets](../repositories/bruin_repository/get_tickets.md)

    * If response status for get tickets is not ok:
      ```python
      logger.warning(
          f"Bad status calling to get ticket for client id: {client_id} and "
          f"ticket id: {ticket_id}. Skipping autoresolve ticket ..."
      )
      ```
      END

    * If there's no ticket data:
          ```python
          logger.info(f"Ticket {ticket_id} couldn't be found in Bruin. Skipping autoresolve...")
          ```
          _Continue with next ticket_
    
    ```python
    logger.info(f"Product category of ticket {ticket_id} from bruin is {product_category}")
    ```

    * If ticket's product category is not whitelisted:
          ```python
          logger.info(
              f"At least one product category of ticket {ticket_id} from the "
              f"following list is not one of the whitelisted categories for "
              f"auto-resolve: {product_category}. Skipping autoresolve ..."
          )
          ```
          _Continue with next ticket_

    ```python
    logger.info(f"Checking to see if ticket {ticket_id} can be autoresolved")
    ```

    [get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)

    * If response status for get ticket details is not ok:
          ```python
          logger.warning(
              f"Bad status calling get ticket details to ticket id: {ticket_id}. Skipping autoresolve ..."
          )
          ```
          END

    * If last outage hasn't been detected recently:
          ```python
          logger.info(
              f"Edge has been in outage state for a long time, so detail {ticket_detail_id} "
              f"(service number {service_number}) of ticket {ticket_id} will not be autoresolved. Skipping "
              f"autoresolve..."
          )
          ```
          _Continue with next ticket_

    * If max auto-resolves threshold has been exceeded:
          ```python
          logger.info(
              f"Limit to autoresolve detail {ticket_detail_id} (service number {service_number}) "
              f"of ticket {ticket_id} has been maxed out already. "
              "Skipping autoresolve..."
          )
          ```
          _Continue with next ticket_

    * If ticket task is resolved already:
          ```python
          logger.info(
              f"Detail {ticket_detail_id} (service number {service_number}) of ticket {ticket_id} is already "
              "resolved. Skipping autoresolve..."
          )
          ```
          _Continue with next ticket_
    
    * If environment is not `PRODUCTION`:
          ```python
          logger.info(
              f"Skipping autoresolve for service number {service_number} "
              f"since the current environment is not production"
          )
          ```
          _Continue with next ticket_

    [unpause_ticket_detail](../repositories/bruin_repository/unpause_ticket_detail.md)

    [resolve_ticket](../repositories/bruin_repository/resolve_ticket.md)

    * If response status for resolve ticket is not ok:
          ```python
          logger.warning(f"Bad status calling to resolve ticket: {ticket_id}. Skipping autoresolve ...")
          ```
          END

    ```python
    logger.info(
        f"Outage ticket {ticket_id} for service_number {service_number} was autoresolved through InterMapper "
        f"emails. Ticket details at https://app.bruin.com/t/{ticket_id}."
    )
    ```
    [append_autoresolve_note_to_ticket](../repositories/bruin_repository/append_autoresolve_note_to_ticket.md)

    ```python
    logger.info(
        f"Detail {ticket_detail_id} (service number {service_number}) of ticket {ticket_id} was autoresolved!"
    )
    ```

    [_remove_job_for_autoresolved_task](_remove_job_for_autoresolved_task.md) (`HNOC Investigate` queue)

    [_remove_job_for_autoresolved_task](_remove_job_for_autoresolved_task.md) (`IPA Investigate` queue)