## Get Service Affecting tickets and their details for Reoccurring Trouble Report / Daily Bandwidth Report

```python
logger.info(f"Retrieving affecting tickets between start date: {start_date} and end date: {end_date}")
```

[get_all_affecting_tickets](get_all_affecting_tickets.md)

* If the response is not valid:
  ```python
  logger.error("An error occurred while fetching Service Affecting tickets for reports")
  ```
  END

```python
logger.info(f"Getting ticket details for {len(response['body'])} tickets")
```

* For each ticket:

    [_get_ticket_details](_get_ticket_details.md)

* If any unexpected error happens while getting these tickets or their details:
  ```python
  msg = f"[service-affecting-monitor-reports] Max retries reached getting all tickets for the report."
  logger.error(f"{msg} - exception: {e}")
  ```
  END