## Get ticket details

[get_ticket_details](get_ticket_details.md)

_Details of Service Affecting ticket are retrieved_

* If response status for get details of Service Affecting ticket is `401` or `403`:
  ```python
  logger.exception(f"Error: Retry after few seconds. Status: {ticket_details['status']}")
  ```
  _The call to retrieve details of Service Affecting ticket is retried immediately_

* If response status for get details of Service Affecting ticket is not ok:
  ```python
  logger.error(f"Error: an error occurred retrieving ticket details for ticket: {ticket_id}")
  ```
  END
* Otherwise:
  ```python
  logger.info(f"Returning ticket details of ticket: {ticket_id}")
  ```
  END

* If all the retries to get details of Service Affecting ticket are used:
  ```python
  msg = (
      f"[service-affecting-monitor-reports]"
      f"Max retries reached getting ticket details {ticket['ticketID']}"
  )
  logger.error(msg)
  ```
  END