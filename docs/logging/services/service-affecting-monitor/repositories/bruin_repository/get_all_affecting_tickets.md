## Get all Service Affecting tickets for Reoccurring Trouble Report / Daily Bandwidth Report

_Service Affecting tickets are retrieved_

* If response status for get Service Affecting tickets is `401` or `403`:
  ```python
  logger.exception(
      f"Error: Retry after few seconds all tickets. Status: {response_all_tickets['status']}"
  )
  ```
  _The call to retrieve Service Affecting tickets is retried immediately_

* If response status for get Service Affecting tickets is not ok:
  ```python
  logger.error(f"Error: an error occurred retrieving affecting tickets: {response_all_tickets}")
  ```
  END

* If all the retries to get Service Affecting tickets are used:
  ```python
  msg = f"Max retries reached getting all tickets for the service affecting monitor process."
  logger.error(f"{msg} - exception: {e}")
  ```
  END