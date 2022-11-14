## Get in-progress ticket tasks for Service Outage ticket

```python
logger.info(f"Getting tasks for ticket {ticket_id}...")
```

[get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
      f"Skipping getting tasks..."
  )
  ```
  END

* If the ticket doesn't have any ticket task:
  ```python
  logger.warning(
      f"Ticket {ticket_id} doesn't have any task under ticketDetails key. "
      f"Skipping getting tasks..."
  )
  ```
  END

```python
logger.info(f"Got tasks for ticket {ticket_id}!")
```

* If an unexpected error happens at some point:
  ```python
  logger.error(f"An error occurred while trying to get ticket tasks for ticket {ticket_id} -> {e}")
  ```