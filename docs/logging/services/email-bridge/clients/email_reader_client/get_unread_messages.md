## Get unread messages

  [login](login.md)

* If there is an error while connecting to the email server:
  ```python
  logger.error(
    f"Cannot obtain unread messages due to current email server being None. "
    f"Returning empty list of unread messages"
  )
  ```
  END

* If there are not any new emails:
  ```python
  logger.info("No unread messages found")
  ```
  END

  [search_messages](search_messages.md)
  
Fetch all the emails from the email server given the constraints

* If there is an error while fetching the emails:
  ```python
  logger.error(f"Error while getting unread messages: FETCH response code is not OK")
  ```
  END

Build response with emails

  [get_body](get_body.md)  


  [logout](logout.md)
